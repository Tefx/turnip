import sys; sys.path.append("..")

from filesystem import LocalFileSystem, FSFilter
from crypto import CryptoFilter

def test():
	class CryptoLocalFS(CryptoFilter, LocalFileSystem):
		def __init__(self, root, passwd):
			CryptoFilter.__init__(self, passwd)
			LocalFileSystem.__init__(self, root)

	cfs = CryptoLocalFS("root", "12345")
	cfs.copy_from_local("../../DFC", "/")
	cfs.copy_to_local("/", "../../test")
	cfs.delete("/")

if __name__ == '__main__':
	test()