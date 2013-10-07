import filesystem
import cStringIO

class CloudFileSystem(filesystem.FileSystemBase):
	def __init__(self, storage, bucket):
		filesystem.FileSystemBase.__init__(self)
		self.storage = storage
		if not self.storage.exists(bucket):
			self.storage.create_bucket(bucket)
		self.bucket = bucket
		self.dir_buf = {}

	def uupdate(self, uuid, f):
		self.storage.upload(f, self.bucket, uuid)

	def uget(self, uuid, f):
		self.storage.download(self.bucket, uuid, f)

	def udelete(self, uuid):
		self.storage.delete_object(self.bucket, uuid)

	def uexists(self, uuid):
		return self.storage.exists(self.bucket, uuid)