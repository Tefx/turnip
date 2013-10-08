import sys; sys.path.append("..")

from filesystem import CodeFileSystem, FSFilter
from crypto import CryptoFilter

def test():
	class CryptoCloudFS(CryptoFilter, CodeFileSystem):
		def __init__(self, conf, k, m, passwd):
			CryptoFilter.__init__(self, passwd)
			CodeFileSystem.__init__(self, conf.gen_stors(), k, m)

	import sys; sys.path.append("..")
	import config
	conf = config.Config("../config.yml")

	cfs = CryptoCloudFS(conf, conf.RSCoding["k"], conf.RSCoding["m"], str(conf.Encryption["key"]))
	cfs.mkfs()
	cfs.copy_from_local("../../sample", "/")
	# cfs.copy_to_local("/", "../../test")
	# cfs.delete("/")

if __name__ == '__main__':
	test()