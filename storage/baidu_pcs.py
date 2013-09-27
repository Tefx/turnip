import storage
from baidupcs import PCS
import os

class BaiduPCS(storage.DiskStorageBase):
	def _connect(self):
		self.pcs = PCS(self.config["access_token"])

	def _check_error(self, resp):
		if resp.ok:
			try:
				return resp.json()
			except:
				pass
		else:
			try:
				msg = resp.json()
			except:
				raise storage.StorageFail(resp.content)
			if "error_code" in msg:
				raise storage.StorageFail(msg["error_msg"])
			else:
				raise storage.StorageFail(resp.state)

	def free(self):
		resp = self.pcs.info()
		msg = self._check_error(resp)
		return msg["quota"] - msg["used"]

	def _upload(self, infile, path):
		return self.pcs.upload(path, infile, ondup="overwrite")

	def _download(self, path, outfile):
		resp = self.pcs.download(path)
		self._check_error(resp)
		for chunk in resp.iter_content(chunk_size=1024):
			if chunk:
				outfile.write(chunk)

	def _get_contents(self, resp):
		return resp["list"]

	def _is_dir(self, item):
		return item["isdir"]

	def _get_path(self, item):
		return item["path"]

	def _meta(self, path):
		return self.pcs.list_files(path)

	def _mkdir(self, path):
		return self.pcs.mkdir(path)

	def _delete(self, path):
		return self.pcs.delete(path)

if __name__ == '__main__':
	conf = {
	  	'root': '/apps/COC/',
		'access_token': '3.0e71baf733d5d95c06c07eaab4725b15.2592000.1381845390.3878778573-1344111', 
		'type': 'baidu_pcs', 
		'refresh_token': '4.f9792103b851d7fe28db8189155a630a.315360000.1694613390.3878778573-1344111'
		}
	pcs = BaiduPCS(conf)
	pcs.create_bucket("bucket")
	print [x for x in pcs.list_buckets()]
	with open(__file__) as f:
		pcs.upload(f, "bucket", "test")
	print [x for x in pcs.list_objects("bucket")]
	with open("test", "w") as f:
		pcs.download("bucket", "test", f)
	pcs.delete_object("bucket", "test")
	print [x for x in pcs.list_objects("bucket")]
	pcs.delete_bucket("bucket")
	print [x for x in pcs.list_buckets()]
