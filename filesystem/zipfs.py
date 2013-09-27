from filesystem import FileSystemBase
import json
import zipfile

class ZipFileSystem(FileSystemBase):
	def __init__(self, f):
		self.zip = zipfile.ZipFile(f, "w")

	def uexists(self, uuid):
		try:
			self.zip.getinfo(uuid)
			return True
		except KeyError:
			return False

	def uupdate(self, uuid, f):
		self.zip.writestr(uuid, f.read())

	def uget(self, uuid, f):
		f.write(self.zip.read(uuid))

	def udelete(self, uuid):
		pass

if __name__ == '__main__':
	fs = ZipFileSystem("fs.zip")
	fs.mknod("/")
	# print fs.get("/")
	# print fs.list("/")
	fs.mknod("/dir_a", True)
	# print fs.get("/")
	# print fs.list("/")
	fs.mknod("/dir_a/b")
	fs.update("/dir_a/b", "test")
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