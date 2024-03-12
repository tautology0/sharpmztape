#!/usr/bin/env python3

import wave
import math
import sys
from bitstream import BitStream
from hexdump import hexdump
from tqdm import tqdm

class FileHeader:
	def __init__(self, raw):
		self.attribute=raw[0]
		self.filename=raw[1:18].decode("cp437").strip()
		self.size=int.from_bytes(raw[18:20],"little")
		self.load=int.from_bytes(raw[20:22],"little")
		self.exec=int.from_bytes(raw[22:24],"little")
		self.comment=raw[24:]
		
	def __str__(self):
		types=[ "unknown", "Machine code program", "MZ-80 BASIC program", "MZ-80 data",
				  "MZ-700 data", "MZ-700 BASIC program" ]
		output =f"Type:     {types[self.attribute]}\n"
		output+=f"Filename: {self.filename}\n"
		output+=f"Size:     ${self.size:04x}\n"
		output+=f"Load:     ${self.load:04x}\n"
		output+=f"Exec:     ${self.exec:04x}\n"
		output+=f"Comment:  {self.comment}\n"
		return output

def converttosharpascii(raw):
	out=b''
	for byte in raw:
		add=byte.to_bytes(1, "little")
		if str(byte) in sharpascii:
			add=sharpascii[str(byte)].encode()
		out+=add
	
	return out
		
def read_pulse(wfile, skip):
	value=0
	repeat=True
	try:
		while repeat:
			# look for the minima - i.e. the value is > the last one
			ovalue=wfile.readframes(1)[0]
			read_edge=wfile.readframes(1)[0]
			while read_edge <= ovalue:
				ovalue=read_edge
				read_edge=wfile.readframes(1)[0]
			# now count the frames to the maxima
			minima=ovalue
			fcount=0
			ovalue=read_edge
			read_edge=wfile.readframes(1)[0]		
			while read_edge >= ovalue:
				fcount+=1
				ovalue=read_edge
				read_edge=wfile.readframes(1)[0]
			maxima=ovalue
			if (maxima - minima) > threshold:
				repeat=False
			
		if fcount > skip:
			value=1
	except:
		# end of stream
		value=-1

	return value

def read_byte(tape):
	bytes=tape.read(bool,9)[1:]
	bytes.reverse()
	num=0
	for j in range(0,len(bytes)):
		num+=int(bytes[j])<<j
		
	return num
	
def read_16bit(tape):
	return (read_byte(tape)<<8)+read_byte(tape)
	
def read_gap(tape):
	GAP=[]
	bit=tape.read(bool,1)[0]
	while bit == True:
		bit=tape.read(bool,1)[0]
	while bit == False:
		GAP.append(bit)
		bit=tape.read(bool,1)[0]
		
	return len(GAP)

def read_tapeheader(tape, commentsize=104):
	gaplength=read_gap(tape)
	if (gaplength < 22000):
		print(f"LGAP was {gaplength} pulses")
		
	LTM=tape.read(bool,79)
	L=tape.read(bool,1)

	# As each byte is preceded by a long pulse, we need to do this manually
	raw=bytearray()
	for i in range(0,24+commentsize):
		raw.append(read_byte(tape))

	header=FileHeader(raw)
	CHKH=read_16bit(tape)
	L=tape.read(bool,1)
	S256=tape.read(bool,256)
	if True in S256:
		print("S256 is not valid")
		
	sraw=bytearray()
	for i in range(0,24+commentsize):
		sraw.append(read_byte(tape))
	sheader=FileHeader(sraw)
	CHKH=read_16bit(tape)
	L=tape.read(bool,1)
	return header
	
def read_file(tape, size):
	gaplength=read_gap(tape)
	if (gaplength < 11000):
		print(f"SGAP was {gaplength} pulses")
		
	STM=tape.read(bool,39)
	L=tape.read(bool,1)

	# Read the tape header
	# As each byte is preceded by a long pulse, we need to do this manually
	raw=bytearray()
	for i in range(0,size):
		raw.append(read_byte(tape))
	return raw
	CHKF=read_16bit(tape)
	L=tape.read(bool,1)
	S256=tape.read(bool,256)
	if True in S256:
		print("S256 is not valid")
		print(S256)
		exit(1)
	craw=bytearray()
	for i in range(0,size):
		craw.append(read_byte(tape))

	CHKF=read_16bit(tape)
	L=tape.read(bool,1)
	return raw
	
def read_datafile(tape):
	block=0
	raw=bytearray()
	while block != 65535:
		gaplength=read_gap(tape)
		if (gaplength < 11000):
			print(f"SGAP was {gaplength} pulses")
			
		STM=tape.read(bool,39)
		L=tape.read(bool,1)
		block=read_16bit(tape)
		for i in range(0,256):
			raw.append(read_byte(tape))

		CHKF=read_16bit(tape)
		L=tape.read(bool,1)
		S256=tape.read(bool,256)
		if True in S256:
			print("S256 is not valid")
			print(S256)
		dummy=read_16bit(tape)
		craw=bytearray()
		for i in range(0,256):
			craw.append(read_byte(tape))
		CHKF=read_16bit(tape)
		L=tape.read(bool,1)
		
	return raw

wfile=wave.open(sys.argv[1],"rb")

# Work out skips depending on the sample rate
# For MZ-700 the sample time is 368 microseconds
skip=math.floor(0.000368*float(wfile.getframerate()))-1
threshold=20
loopit=True
short_frame=0
long_frame=0

# Table to decode sharpascii in strings
sharpascii={}
sharpascii['146']='e'; sharpascii['147']='~'; sharpascii['148']='~'; sharpascii['150']='t';
sharpascii['151']='g'; sharpascii['152']='h'; sharpascii['154']='b'; sharpascii['155']='x';
sharpascii['156']='d'; sharpascii['157']='r'; sharpascii['158']='p'; sharpascii['159']='c';
sharpascii['160']='q'; sharpascii['161']='a'; sharpascii['162']='z'; sharpascii['163']='w';
sharpascii['164']='s'; sharpascii['165']='u'; sharpascii['166']='i'; sharpascii['169']='k';
sharpascii['170']='f'; sharpascii['171']='v'; sharpascii['175']='j'; sharpascii['176']='n';
sharpascii['179']='m'; sharpascii['183']='o'; sharpascii['184']='l'; sharpascii['189']='y';

tape=BitStream()
# read all the file into a Bitstream
print("Converting tape to bits")
bit=0
with tqdm(total=100) as pbar:
	while bit >= 0:
		bit=read_pulse(wfile, skip)
		if bit != -1:
			tape.write(bit,bool)
		pbar.n=int((wfile.tell() / wfile.getnframes())*100)
		pbar.refresh()
		
print("Header for first file")
header=read_tapeheader(tape)
print(header)
print(f"Extracting {header.filename} as {header.filename}1.dat")
raw=read_datafile(tape)
with open(f"{header.filename}1.dat","wb") as fout:
	fout.write(raw)

print("Header for second file")
header=read_tapeheader(tape)
print(f"Extracting {header.filename} as {header.filename}2.dat")
raw=read_datafile(tape)
with open(f"{header.filename}2.dat","wb") as fout:
	fout.write(raw)

