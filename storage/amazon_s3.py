import storage
from boto.s3.connection import S3Connection
from boto.s3.connection import Location
from boto.s3.key import Key

class AmazonS3(storage.StorageBase):
	def __init__(self, *args):
		super(AmazonS3, self).__init__(*args)
		self.s3 = S3Connection(self.config["access_key_id"], self.config["secret_access_key"])
		self.location = getattr(Location, self.config["location"])

	def upload(self, infile, bucket, name):
		if isinstance(bucket, storage.Bucket):
			bucket = bucket.name
		bucket = self.s3.get_bucket(bucket)
		k = Key(bucket)
		k.key = name
		k.set_contents_from_file(infile)

	def download(self, bucket, name, outfile):
		if isinstance(bucket, storage.Bucket):
			bucket = bucket.name
		bucket = self.s3.get_bucket(bucket)
		k = Key(bucket)
		k.key = name
		k.get_contents_to_file(outfile)

	def list_objects(self, bucket):
		if isinstance(bucket, storage.Bucket):
			bucket = bucket.name
		bucket = self.s3.get_bucket(bucket)
		for key in bucket.list():
			yield storage.Object(self, {"name":key.key, "bucket":bucket.name})

	def list_buckets(self):
		for bucket in self.s3.get_all_buckets():
			yield storage.Bucket(self, {"name":bucket.name})

	def create_bucket(self, name):
		self.s3.create_bucket(name, location=self.location)
		return storage.Bucket(self, {"name":name})

	def delete_bucket(self, name):
		if isinstance(name, storage.Bucket):
			name = name.name
		bucket = self.s3.get_bucket(name)
		for key in bucket.list():
			key.delete()
		self.s3.delete_bucket(name)

	def delete_object(self, bucket, name):
		if isinstance(bucket, storage.Bucket):
			bucket = bucket.name
		bucket = self.s3.get_bucket(bucket)
		bucket.delete_key(name)

if __name__ == '__main__':
	conf = {
		'type': 'amazon_s3', 
		'secret_access_key': 'TLjoEtcPwryEbBI1pOjerEIcSlTmrlmOAow8yYPo', 'location': 'APNortheast', 
		'access_key_id': 'AKIAIQONMGWDJGQG3BPA'
	}
	s = AmazonS3(conf)
	s.create_bucket("tefxzzmbucket")
	print [x for x in s.list_buckets()]
	with open(__file__) as f:
		s.upload(f, "tefxzzmbucket", "testobject")
	print [x for x in s.list_objects("tefxzzmbucket")]
	with open("test1", "w") as f:
		s.download("tefxzzmbucket", "testobject", f)
	s.delete_object("tefxzzmbucket", "testobject")
	print [x for x in s.list_objects("tefxzzmbucket")]
	s.delete_bucket("tefxzzmbucket")
	print [x for x in s.list_buckets()]


