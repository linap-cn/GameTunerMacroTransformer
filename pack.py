#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import zlib,sys

def getfilelength(fileobj):
	fileobj.seek(0,2);
	filelength=fileobj.tell()
	fileobj.seek(0,0);
	return filelength
if __name__=="__main__":
	if len(sys.argv)<3:
		print("usage: python3 pack.py [inputfile] [outputfile]")
		sys.exit(1)
	inputfile=sys.argv[1]
	outputfile=sys.argv[2]

	with open(inputfile,"rb") as filein,open(outputfile,"wb") as fileout:
		filein.seek(0,2);
		filelength=filein.tell()
		filein.seek(0,0);
		data=filein.read(filelength)
		bytesdata=b""
		try:
			bytesdata=zlib.decompress(data,0)
		except zlib.error:
			bytesdata=zlib.compress(data)
		finally:
			fileout.write(bytesdata)
