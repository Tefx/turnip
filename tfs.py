#!/usr/bin/env python
# -*- coding: utf-8 -*-

from filesystem import CodeFileSystem
from crypto import CryptoFilter
import config
import argparse
import posixpath
import os

class CryptoCloudFS(CryptoFilter, CodeFileSystem):
	def __init__(self, conf, k, m, passwd):
		CryptoFilter.__init__(self, passwd)
		CodeFileSystem.__init__(self, conf.gen_stors(), k, m)

# def _get_path(self, path=None):
# 	if path == "":
# 		return self.pwd
# 	elif path[0] == "/":
# 		return path
# 	else:
# 		return posixpath.join(self.pwd, path)

def ls(fs, path):
	print " ".join(fs.list(path))

def mkdir(fs, path):
	fs.mknod(path, isdir=True)
	fs.sync()

def put(fs, path, srcpath):
	if path[-1] == "/":
		path = posixpath.join(path, os.path.split(os.path.abspath(srcpath))[1])
	else:
		path
	fs.mknod(path)
	with open(srcpath, "rb") as f:
		fs.update(path, f)
	fs.sync()

def get(fs, path, destpath):
	with open(destpath, "wb") as f:
		fs.get(path, f)

def cat(fs, path):
	print fs.get(path)

def rm(fs, path):
	fs.delete(path)
	fs.sync()

def copylocal(fs, path, localpath):
	fs.copy_from_local(localpath, path)

def copy2local(fs, path, localpath):
	fs.copy_to_local(path, localpath)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("cmd")
	parser.add_argument("path", default="/", nargs="?")
	parser.add_argument("localpath", default=None, nargs="?")
	args = parser.parse_args()
	conf = config.Config("config.yml")

	cfs = CryptoCloudFS(conf, conf.RSCoding["k"], conf.RSCoding["m"], str(conf.Encryption["key"]))
	if args.localpath:
		globals()[args.cmd](cfs, args.path, args.localpath)
	else:
		globals()[args.cmd](cfs, args.path)

