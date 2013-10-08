from gevent import monkey; monkey.patch_all()
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import storage

class Config(object):
	def __init__(self, conf_file):
		with open(conf_file) as f:
			self.data = load(f.read(), Loader=Loader)

	def gen_stors(self):
		for conf in self.data["Storages"]:
			try:
				stor = getattr(storage, conf["type"])(conf)
				yield stor, conf
			except:
				pass

	def __getattr__(self, field):
		return self.data[field]

if __name__ == '__main__':
	config = Config("config.yml")
	print config.gen_stors()
