from gevent import monkey; monkey.patch_all()
import gevent
import filesystem
import zfec
import os
import tempfile
import shutil

class Coder(object):
	def __init__(self, k, m):
		super(Coder, self).__init__()
		self.k = k
		self.m = m
		self.tempdir = tempfile.mkdtemp("_turnip")

	def get_size(self, obj):
		pos = 0
		if hasattr(obj, 'tell'):
			pos = obj.tell()
		if hasattr(obj, "getvalue"):
			raw_data = obj.getvalue()
			if pos == 0:
				return len(raw_data)
			else:
				return max(0, len(raw_data) - pos)
		elif hasattr(obj, 'fileno'):
			return max(0, os.fstat(obj.fileno()).st_size - pos)
		elif hasattr(obj, '__len__'):
			return max(0, len(obj) - pos)
		else:
			return len(obj.read())

	def encode(self, uuid, inf):
		zfec.filefec.encode_to_files(inf, self.get_size(inf), self.tempdir, uuid, self.k, self.m)
		mlen = len(str(self.m))
		format = zfec.filefec.FORMAT_FORMAT % (mlen, mlen,)
		for shnum in range(self.m):
			fname = os.path.join(self.tempdir, format % (uuid, shnum, self.m, ".fec",))
			f = open(fname, "rb")
			os.unlink(fname)
			yield f

	def decode(self, f, infs):
		for fp in infs:
			fp.seek(0)
		zfec.filefec.decode_from_files(f, infs)

	def gen_temp_files(self, uuid):
		mlen = len(str(self.m))
		format = zfec.filefec.FORMAT_FORMAT % (mlen, mlen,)
		for shnum in range(self.m):
			fname = os.path.join(self.tempdir, format % (uuid, shnum, self.m, ".fec",))
			f = open(fname, "w+b")
			os.unlink(fname)
			yield f

	def __del__(self):
		shutil.rmtree(self.tempdir)

class FirstNEvent(object):
	def __init__(self, n):
		self.left = n
		self.event = gevent.event.Event()
		self.event.clear()

	def set(self):
		self.left -= 1
		if not self.left:
			self.event.set()

	def wait(self):
		self.event.wait()

class CodeFileSystem(filesystem.FileSystemBase):
	def __init__(self, stors, k, m):
		filesystem.FileSystemBase.__init__(self)
		self.stors = []
		for stor, conf in stors:
			self.stors.append(stor)
			stor._codefs_bucket = conf["bucket"]
			if not stor.exists(stor._codefs_bucket):
				stor.create_bucket(stor._codefs_bucket)
		self.m = min(m, len(self.stors))
		self.k = min(k, m)
		self.coder = Coder(k, m)

	def stor_try(self, stor, method, event, *args):
		try:
			res = getattr(stor, method)(*args)
			if event:
				event.set()
			return res
		except Exception, e:
			return e

	def uupdate(self, uuid, f):
		fps = self.coder.encode(uuid, f)
		jobs = []
		for stor, fp in zip(self.stors, fps):
			jobs.append(gevent.spawn(self.stor_try, stor, "upload", None, fp, stor._codefs_bucket, uuid))
		gevent.joinall(jobs)
		if sum([1 for job in jobs if not isinstance(job.value, Exception)]) < self.k:
			raise Exception("Failed, less than %d parts have been uploaded." % self.k)

	def uget(self, uuid, f):
		temp_fps = list(self.coder.gen_temp_files(uuid))
		jobs = []
		ready = FirstNEvent(self.k)
		for stor, fp in zip(self.stors, temp_fps):
			jobs.append(gevent.spawn(self.stor_try, stor, "download", ready, stor._codefs_bucket, uuid, fp))
		ready.wait()
		fps = [temp_fps[i] for i in range(len(temp_fps)) if jobs[i].ready() and not isinstance(jobs[i].value, Exception)]
		gevent.killall(jobs)
		if len(fps) < self.k:
			raise Exception("Failed, less than %d parts have been downloaded." % self.k)
		self.coder.decode(f, fps)

	def udelete(self, uuid):
		jobs = []
		for stor in self.stors:
			jobs.append(gevent.spawn(self.stor_try, stor, "delete_object", None, stor._codefs_bucket, uuid))
		gevent.joinall(jobs)

	def uexists(self, uuid):
		jobs = []
		for stor in self.stors:
			jobs.append(gevent.spawn(self.stor_try, stor, "exists", None, stor._codefs_bucket, uuid))
		gevent.joinall(jobs)
		return [job.value for job in jobs if job.ready()].count(True) >= self.k

if __name__ == '__main__':
	import sys; sys.path.append("..")
	import config
	conf = config.Config("../config.yml")
	cfs = CodeFileSystem(conf.gen_stors(), 2, 3)
	cfs.mkfs()
	cfs.copy_from_local("../../sample", "/")
	# cfs.copy_from_local("../../sample", "/apiclient/")
	# print cfs.exists("/")
	# print cfs.exists("/aaa")
	cfs.copy_to_local("/", "../../test")
	cfs.delete("/")
