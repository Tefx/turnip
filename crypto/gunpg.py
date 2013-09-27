import gnupg

class GnuPGEngine(object):
	def __init__(self, gnupghome):
		self.gnupghome = gnupghome
		self.gpg = gnupg.GPG(gnupghome=gnupghome)
		self.gpg.encoding='utf-8'

	def generate_key(self, name):
		input_data = self.gpg.gen_key_input(name_real=name)
		key = self.gpg.gen_key(input_data)
		return key.fingerprint

	def encrypt(self, data, fingerprint):
		return self.gpg.encrypt(data, fingerprint)

if __name__ == '__main__':
	gpg = GnuPGEngine("./gpg")
	# print gpg.generate_key("zzm")
	data = gpg.encrypt("test", "800C2E596922E951179CBA9F4B90702519EA8721")
	print type(data)