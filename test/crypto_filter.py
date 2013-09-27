import sys; sys.path.append("..")

from filesystem import localfs, FSFilter
from crypto import cipher

def test():
	class CryptoLocalFS(cipher.CryptoFilter, localfs.LocalFileSystem):
		def __init__(self, root, passwd):
			cipher.CryptoFilter.__init__(self, passwd)
			localfs.LocalFileSystem.__init__(self, root)

	cfs = CryptoLocalFS("root", "12345")
	cfs.copy_from_local("../../DFC", "/")
	cfs.copy_to_local("/", "../../test")
	cfs.delete("/")

if __name__ == '__main__':
	test()