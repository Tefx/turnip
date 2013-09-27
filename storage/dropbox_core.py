import storage
import dropbox

class Dropbox(storage.DiskStorageBase):
	def _connect(self):
		self.client = dropbox.client.DropboxClient(self.config["access_token"])

	def free(self):
		info = self.client.account_info()["quota_info"]
		return info["quota"] - info["shared"] - info["normal"]

	def _upload(self, infile, path):
		return self.client.put_file(path, infile)

	def _download(self, path, outfile):
		resp = self.client.get_file(path)
		while True:
			chunk = resp.read(1024)
			if not chunk:
				break
			outfile.write(chunk)

	def _get_contents(self, resp):
		return resp["contents"]

	def _is_dir(self, item):
		return item["is_dir"]

	def _get_path(self, item):
		return item["path"]

	def _meta(self, path):
		return self.client.metadata(path)

	def _mkdir(self, path):
		return self.client.file_create_folder(path)

	def _delete(self, path):
		return self.client.file_delete(path)

if __name__ == '__main__':
	conf = {
		'access_token': '_-Ry1urWHgoAAAAAAAAAAa6fgLl1GdjTH_rHqbXZr29CTWPJJOSRYzwHHzWvKLGR', 
		'type': 'dropbox', 
		'root': '/', 
		'user_id': 4510639
		}
	c = Dropbox(conf)
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

