from uuid import uuid1
import json
import posixpath
import os
import cStringIO

class FileSystemBase(object):
	def __init__(self):
		self.dir_cache = {}

	def uupdate(self, uuid, f):
		pass

	def uget(self, uuid, f):
		pass

	def udelete(self, uuid):
		pass

	def uexists(self, uuid):
		pass

	def sync(self):
		for d, v in self.dir_cache.iteritems():
			self.uupdate_r(d, v, False)
		self.dir_cache = {}

	def uupdate_r(self, uuid, f, caching=True):
		if not hasattr(f, "read"):
			if not isinstance(f, basestring):
				f = json.dumps(f)
			f = cStringIO.StringIO(f)
		if uuid[-4:] == ".dir" and caching:
			self.dir_cache[uuid] = f.read()
		else:
			if hasattr(self, "before_uupdate"):
				uuid, f = self.before_uupdate(uuid, f)
			self.uupdate(uuid, f)
			if hasattr(self, "after_uupdate"):
				uuid, f = self.after_uupdate(uuid, f)

	def uget_r(self, uuid, outf=None):
		if uuid[-4:] == ".dir" and uuid in self.dir_cache:
				return self.dir_cache[uuid]
		if not outf:
			f = cStringIO.StringIO()
		else:
			f = outf
		if hasattr(self, "before_uget"):
			uuid, f = self.before_uget(uuid, f)
		self.uget(uuid, f)
		if hasattr(self, "after_uget"):
			uuid, f = self.after_uget(uuid, f)
		if not outf:
			buf = f.getvalue()
			if uuid[-4:] == ".dir":
				self.dir_cache[uuid] = buf
			return buf

	def mknod(self, path, isdir=False):
		if path == "/":
			self.uupdate_r("root.dir", {"contents":{}, "path":path})
			return
		uuid = uuid1().hex
		if isdir:
			uuid = uuid + ".dir"
		up, name = posixpath.split(path)
		upuuid = self.get_uuid(up)
		d = json.loads(self.uget_r(upuuid))
		if name not in d["contents"]:
			d["contents"][name] = {"uuid":uuid}
		self.uupdate_r(upuuid, d)
		if isdir:
			self.uupdate_r(uuid, {"contents":{}, "path":path})

	def exists(self, path):
		if path == "/":
			return self.uexists("root.dir")
		else:
			up, name = posixpath.split(path)
			return name in self.list(up)

	def list(self, path, info=False):
		uuid = self.get_uuid(path)
		return self.ulist(uuid, info)

	def ulist(self, uuid, info=False):
		meta = self.uget_r(uuid)
		if not info:
			return json.loads(meta)["contents"].keys()
		else:
			return json.loads(meta)["contents"].items()

	def isdir(self, path):
		return self.get_uuid(path)[-4:] == ".dir"

	def uisdir(self, uuid):
		return uuid[-4:] == ".dir"

	def uwalk(self, uuid, path=None):
		names = self.ulist(uuid, True)
		dirs = [name for name, info in names if info["uuid"][-4:] == ".dir"]
		files = [name for name, info in names if name not in dirs]
		if not path:
			path = self.get_path(uuid)
		yield path, dirs, files
		for name, info in names:
			subpath = posixpath.join(path, name)
			if info["uuid"][-4:] == ".dir":
				for r, d, f in self.uwalk(info["uuid"], subpath):
					yield r, d, f

	def walk(self, path):
		uuid = self.get_uuid(path)
		for r, d, f in self.uwalk(uuid, path):
			yield r, d, f

	def update(self, path, f):
		return self.uupdate_r(self.get_uuid(path), f)

	def get(self, path, f=None):
		return self.uget_r(self.get_uuid(path), f)

	def get_uuid(self, path):
		if path == "/":
			return "root.dir"
		up, name = posixpath.split(path)
		if up == "/":
			upuuid = "root.dir"
		else:
			upuuid = self.get_uuid(up)
		d = json.loads(self.uget_r(upuuid))
		if name in d["contents"]:
			return d["contents"][name]["uuid"]
		else:
			return None

	def get_path(self, uuid):
		return json.loads(self.uget_r(uuid))["path"]

	def _udelete(self, uuid):
		if uuid[-4:] == ".dir":
			d = json.loads(self.uget_r(uuid))
			for k,v in d["contents"].iteritems():
				self._udelete(v["uuid"])
		self.udelete(uuid)

	def delete(self, path):
		uuid = self.get_uuid(path)
		self._udelete(uuid)
		if uuid != "root.dir":
			up, name = os.path.posixpath(path)
			upuuid = self.get_uuid(up)
			d = json.loads(self.uget_r(upuuid))
			if name not in d[name]:
				del d["contents"][name]
			self.uupdate_r(upuuid, json.dumps(d))

	def copy_from_local(self, local_path, path):
		len_base = len(os.path.abspath(local_path))+1
		for local_root, dirs, files in os.walk(local_path, True):
			root = "/" + os.path.abspath(local_root)[len_base:]
			root = root.replace(os.path.sep, "/")
			if not self.exists(root):
				self.mknod(root, True)
			for f in files:
				path = posixpath.join(root, f)
				if not self.exists(path):
					self.mknod(path)
				with open(os.path.join(local_root, f)) as inf:
					self.update(path, inf)
		self.sync()

	def copy_to_local(self, path, local_path):
		for root, dirs, files in self.walk(path):
			local_root = os.path.join(local_path, root.strip("/").replace("/", os.path.sep))
			if not os.path.exists(local_root):
				os.mkdir(local_root)
			for f in files:
				path = posixpath.join(root, f)
				with open(os.path.join(local_root, f), "w") as outf:
					self.get(path, outf)	

class FSFilter(object):
	def before_uupdate(self, uuid, f):
		return uuid, f

	def before_uget(self, uuid, f):
		return uuid, f

	def after_uget(self, buf=None):
		return buf
