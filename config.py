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

	def gen_storages(self):
		return {
			conf["id"]: getattr(storage, conf["type"])(conf) \
						for conf in self.data["storages"]
		}

if __name__ == '__main__':
	config = Config("config.yml")
	print config.gen_storages()
