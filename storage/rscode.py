
class CodeStorage(object):
	def __init__(self, config, k, m):
		self.stors = config.gen_storages()
		self.m = m
		self.k = k

	def free(self):
		res = [stor.free() for name, stor in self.stors.iteritems()]
		return sum([x for x in res if x])

	def upload(self, infile, bucket, name):
		pass


if __name__ == '__main__':
	import sys; sys.path.insert(0, "..")
	import config
	cs = CodeStorage(config.Config("../config.yml"))
	print cs.free()