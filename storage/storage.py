class StorageBase(object):
	"""Base class for all storage backends"""
	def __init__(self, config):
		self.config = config

	def free(self):
		pass

	def upload(self, infile, bucket, name):
		pass

	def download(self, bucket, name, outfile):
		pass

	def list_objects(self, bucket):
		pass

	def list_buckets(self):
		pass

	def create_bucket(self, name):
		pass

	def delete_bucket(self, name):
		pass

	def delete_object(self, bucket, name):
		pass

class DiskStorageBase(StorageBase):
	def _check_error(self, resp):
		return resp

	def _connect(self):
		pass

	def _upload(self, infile, path):
		pass

	def _download(self, outfile):
		pass

	def _meta(self, path):
		pass

	def _get_contents(self, resp):
		pass

	def _is_dir(self, item):
		pass

	def _get_path(self, item):
		pass

	def _mkdir(self, path):
		pass

	def _delete(self, path):
		pass

	def __init__(self, *args):
		super(DiskStorageBase, self).__init__(*args)
		self.root = self.config["root"]
		self._connect()

	def upload(self, infile, bucket, name):
		if isinstance(bucket, Bucket):
			bucket = bucket.name
		path = self.root + "/".join([bucket, name])
		resp = self._upload(infile, path)
		self._check_error(resp)

	def download(self, bucket, name, outfile):
		if isinstance(bucket, Bucket):
			bucket = bucket.name
		path = self.root + "/".join([bucket, name])
		self._download(path, outfile)

	def _list(self, path, follow_dir=True):
		path = self.root + path.lstrip("/")
		resp = self._meta(path)
		for item in self._get_contents(self._check_error(resp)):
			item["name"] = self._get_path(item)[len(self.root):]
			if self._is_dir(item) and follow_dir:
				for subitem in self._list(item["name"]):
					yield subitem
			yield item

	def list_objects(self, bucket):
		if isinstance(bucket, Bucket):
			bucket = bucket.name
		for item in self._list(bucket):
			item["bucket"] = Bucket(self, {"name": bucket})
			item["name"] = item["name"][len(bucket):].lstrip("/")
			yield Object(self, item)

	def list_buckets(self):
		for item in self._list("/", False):
			if self._is_dir(item):
				yield Bucket(self, item)

	def create_bucket(self, name):
		path = self.root + name.lstrip("/")
		resp = self._mkdir(path)
		self._check_error(resp)
		return Bucket(self, {"name":name})

	def delete_bucket(self, name):
		if isinstance(name, Bucket):
			name = name.name
		path = self.root + name.lstrip("/")
		resp = self._delete(path)
		self._check_error(resp)

	def delete_object(self, bucket, name):
		if isinstance(bucket, Bucket):
			bucket = bucket.name
		path = self.root + "/".join([bucket, name])
		self._delete(path)

class ObjectOrBucket(object):
	def __repr__(self):
		return "%s:%s" % (self.__class__, self.name)

class Object(ObjectOrBucket):
	def __init__(self, storage, args):
		self.storage = storage
		for attr in ["name", "bucket"]:
			setattr(self, attr, args.get(attr, "UNKNOWN"))

	def update(self, f):
		return self.storage.upload(f, self.bucket.name, self.name)

	def fetch(self, f):
		return self.storage.download(self.bucket.name, self.name, f)

class Bucket(ObjectOrBucket):
	def __init__(self, storage, args):
		self.storage = storage
		for attr in ["name"]:
			setattr(self, attr, args.get(attr, "UNKNOWN"))

	def list(self):
		return [x for x in self.storage.list_objects(self)]

	def __iter__(self):
		for obj in self.list():
			yield obj

	def delete(self, name):
		return self.storage.delete_object(self.name, name)

	def upload(self, f, name):
		return self.storage.upload(f, self.name, name)

	def download(self, name, f):
		return self.storage.download(self.name, name, f)

class StorageFail(Exception):
	"""Storage unavailable error"""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

if __name__ == '__main__':
	# from baidu_pcs import BaiduPCS
	from amazon_s3 import AmazonS3
	# conf = {
	#   	'appname': 'COC',
	# 	'access_token': '3.0e71baf733d5d95c06c07eaab4725b15.2592000.1381845390.3878778573-1344111', 
	# 	'type': 'baidu_pcs', 
	# 	'refresh_token': '4.f9792103b851d7fe28db8189155a630a.315360000.1694613390.3878778573-1344111'
	# 	}
	conf = {
		'type': 'amazon_s3', 
		'secret_access_key': 'TLjoEtcPwryEbBI1pOjerEIcSlTmrlmOAow8yYPo', 'location': 'APNortheast', 
		'access_key_id': 'AKIAIQONMGWDJGQG3BPA'
	}
	s = AmazonS3(conf)
	buckets = s.list_buckets()
	print [x for x in buckets]
	# test_bucket = buckets.next()
	# test_obj = test_bucket.list()[0]
	# with open(__file__) as f:
	# 	test_bucket.upload(f, "test")
	# with open("test", "w") as f:
	# 	test_bucket.download("test", f)
	# test_bucket.delete("test")
	# with open("test", "w") as f:
	# 	test_obj.fetch(f)
	# with open(__file__) as f:
	# 	test_obj.update(f)
		
		