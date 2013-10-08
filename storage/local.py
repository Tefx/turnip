import storage
import os
import shutil

class LocalStorage(storage.DiskStorageBase):
	def free(self):
		st = os.statvfs(self.root)
		return min(self.config["quota"], st.f_bavail * st.f_frsize)

	def _upload(self, infile, path):
		path = path.replace("/", os.path.sep)
		with open(path, "w") as f:
			while True:
				buf = infile.read(1024)
				if not buf:
					break
				f.write(buf)

	def _download(self, path, outfile):
		path = path.replace("/", os.path.sep)
		with open(path) as f:
			while True:
				buf = f.read(1024)
				if not buf:
					break
				outfile.write(buf)

	def _meta(self, path):
		path = path.replace("/", os.path.sep)
		for name in os.listdir(path):
			subpath = os.path.join(path, name)
			yield {"name": name, "path":subpath, "isdir":os.path.isdir(subpath)}

	def _get_contents(self, resp):
		return resp

	def _is_dir(self, item):
		return item["isdir"]

	def _get_path(self, item):
		return item["path"]

	def _mkdir(self, path):
		return os.mkdir(path)

	def _delete(self, path):
		if not os.path.isdir(path):
			return os.remove(path)
		else:
			return shutil.rmtree(path)

if __name__ == '__main__':
	conf = {
		'root': './'
	}
	c = LocalStroage(conf)
	c.create_bucket("bucket")
	print [x for x in c.list_buckets()]
	with open(__file__) as f:
		c.upload(f, "bucket", "test")
	print [x for x in c.list_objects("bucket")]
	with open("test", "w") as f:
		c.download("bucket", "test", f)
	c.delete_object("bucket", "test")
	print [x for x in c.list_objects("bucket")]
	c.delete_bucket("bucket")
	print [x for x in c.list_buckets()]

