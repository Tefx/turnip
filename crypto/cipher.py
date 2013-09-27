from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Hash import SHA256
import json

import sys; sys.path.append("../filesystem"); import filesystem

class AESWrapper(object):
	def __init__(self, fp, key):
		self.fp = fp
		self.key = key
		self.read_cipher = None
		self.write_cipher = None

	def close(self):
		self.fp.close()

	def read(self, size=-1):
		buf = self.fp.read(size)
		if not self.read_cipher:
			ctr = Counter.new(128)
			self.read_cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
		return self.read_cipher.encrypt(buf)

	def write(self, buf):
		if not self.write_cipher:
			ctr = Counter.new(128)
			self.write_cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
		return self.fp.write(self.write_cipher.encrypt(buf))

class CryptoFilter(filesystem.FSFilter):
	def __init__(self, password):
		filesystem.FSFilter.__init__(self)
		h = SHA256.new(password)
		bytes = h.digest()
		self.key = bytes[AES.block_size:]

	def before_uupdate(self, uuid, f):
		if hasattr(f, "read"):
			return uuid, AESWrapper(f, self.key)
		elif not isinstance(f, basestring):
			ctr = Counter.new(128)
			cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
			return uuid, cipher.encrypt(json.dumps(f))
		else:
			ctr = Counter.new(128)
			cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
			return uuid, cipher.encrypt(f)

	def before_uget(self, uuid, f):
		return uuid, AESWrapper(f, self.key)


