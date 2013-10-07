import sys; sys.path.append("..")

from filesystem import CloudFileSystem
from crypto import CryptoFilter
import config

def test():
	class CryptoCloudFS(CryptoFilter, CloudFileSystem):
		def __init__(self, storage, bucket, passwd):
			CryptoFilter.__init__(self, passwd)
			CloudFileSystem.__init__(self, storage, bucket)

	storages = config.Config("../config.yml").gen_storages()
	# fs = CloudFileSystem(storages["dropbox"], "tefxzzmroottest")
	fs = CryptoCloudFS(storages["dropbox"], "tefxzzmroottest", "88580323")
	fs.copy_from_local("../../drive", "/")
	fs.copy_to_local("/", "../../test")
	fs.delete("/")

if __name__ == '__main__':
	test()