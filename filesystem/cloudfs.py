import filesystem

class CloudFileSystem(filesystem.FileSystemBase):
	def __init__(self, storage, bucket):
		self.storage = storage
		if not self.storage.exists(bucket):
			self.storage.create_bucket(bucket)
		self.bucket = bucket

	def uupdate(self, uuid, f):
		self.storage.upload(f, self.bucket, uuid)

	def uget(self, uuid, f):
		self.storage.download(self.bucket, uuid, f)

	def udelete(self, uuid):
		self.storage.delete_object(self.bucket, uuid)

	def uexists(self, uuid):
		return self.storage.exists(self.bucket, uuid)


if __name__ == '__main__':
	import sys; sys.path.append("../")
	from storage import LocalStorage

	conf = {
		'root': './'
	}
	fs = CloudFileSystem(LocalStorage(conf), "root")
	fs.copy_from_local("../../DFC", "/")
	fs.copy_to_local("/", "../../test")
	# for path, dirs, files in fs.walk("/"):
	# 	print path, dirs, files
	fs.delete("/")