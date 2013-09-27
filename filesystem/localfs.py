from filesystem import FileSystemBase
import os
import json

class LocalFileSystem(FileSystemBase):
	def __init__(self, store_location):
		self.root = store_location
		if not os.path.exists(self.root):
			os.mkdir(self.root)

	def uexists(self, uuid):
		path = os.path.join(self.root, uuid)
		return os.path.exists(path)

	def uupdate(self, uuid, f):
		path = os.path.join(self.root, uuid)
		with open(path, "w") as outf:
			if hasattr(f, "read"):
				outf.write(f.read())
			elif not isinstance(f, basestring):
				outf.write(json.dumps(f))
			else:
				outf.write(f)

	def uget(self, uuid, f=None):
		path = os.path.join(self.root, uuid)
		with open(path) as inf:
			if f:
				f.write(inf.read())
			else:
				return inf.read()

	def udelete(self, uuid):
		path = os.path.join(self.root, uuid)
		if os.path.exists(path):
			os.remove(path)

if __name__ == '__main__':
	fs = LocalFileSystem("root")
	# fs.mknod("/")
	# # print fs.get("/")
	# # print fs.list("/")
	# fs.mknod("/dir_a", True)
	# # print fs.get("/")
	# # print fs.list("/")
	# fs.mknod("/dir_a/b")
	# fs.update("/dir_a/b", "test")
	# print fs.get("/dir_a")
	# print fs.list("/dir_a")
	# print fs.exists("/dir_a/b")
	# print fs.exists("/dir_a/c")
	# print fs.get("/dir_a/b")

	# fs.delete("/")
	# for root, dirs, files in os.walk("./", True):
	# 	print root, dirs, files
	fs.copy_from_local("../../DFC", "/")
	fs.copy_to_local("/", "../../test")
	# for path, dirs, files in fs.walk("/"):
	# 	print path, dirs, files
	fs.delete("/")