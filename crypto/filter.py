import sys; sys.path.append("../filesystem")
import cipher
import filesystem

class CryptoFilter(filesystem.FSFilter):
	def __init__(self, password):
		super(CryptoFilter, self).__init__()
		self.key = cipher.gen_key(password)

	def before_uupdate(self, uuid, f):
		return uuid, cipher.AESWrapper(f, self.key)

	def before_uget(self, uuid, f):
		if f != None:
			return uuid, cipher.AESWrapper(f, self.key)
		else:
			return uuid, None

	def after_uget(self, buf=None):
		if buf:
			return cipher.crypto(buf)
		else:
			return buf
