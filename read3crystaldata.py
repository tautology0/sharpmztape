#!/usr/bin/env python3
from tqdm import tqdm

class Room:
	def __init__(self, name, description):
		self.name=name
		self.description=description
		
	def __str__(self):
		output=f"Room: {self.name}\n"
		output+=expanddescription(self.description)
		return output

sharpascii={}
sharpascii['146']='e'; sharpascii['147']='~'; sharpascii['148']='~'; sharpascii['150']='t'; sharpascii['151']='g'; sharpascii['152']='h'; sharpascii['154']='b';
sharpascii['155']='x'; sharpascii['156']='d'; sharpascii['157']='r'; sharpascii['158']='p'; sharpascii['159']='c';
sharpascii['160']='q'; sharpascii['161']='a'; sharpascii['162']='z'; sharpascii['163']='w'; sharpascii['164']='s';
sharpascii['165']='u'; sharpascii['166']='i'; sharpascii['169']='k'; sharpascii['170']='f'; sharpascii['171']='v';
sharpascii['175']='j'; sharpascii['176']='n'; sharpascii['179']='m'; sharpascii['183']='o'; sharpascii['184']='l';
sharpascii['189']='y';

def expanddescription(string):
	output=""
	i=0
	while i < len(string):
		r=string[i]
		i+=1
		if r == '/':
			r = dictionary[ord(string[i])-66]
			i+=1
		output+=r
	# split the output into groups of 40 and regroup
	split=[output[i:i+40] for i in range(0, len(output), 40)]
	return '\n'.join(split)

def converttosharpascii(raw):
	out=b''
	for byte in raw:
		add=byte.to_bytes(1, "little")
		if str(byte) in sharpascii:
			add=sharpascii[str(byte)].encode()
		out+=add
	
	return out

def read_string(fin):
	raw=bytearray()
	b=b'\0'
	while b != b'\r' and b != b'\x1a':
		b=fin.read(1)
		if b != b'\r': raw+=b
	return converttosharpascii(raw).decode()

nrooms=165
nwords=91
ndict=25

fin=open('DATA1.dat','rb')
rooms=[]
for i in range(nrooms):
	room=Room(read_string(fin), read_string(fin))
	rooms.append(room)
	
words=[]
for i in range(nwords):
	word=read_string(fin)
	words.append(word)
	
dictionary=[]
for i in range(ndict):
	dict=read_string(fin)
	dictionary.append(dict)
	
for room in rooms:
	print(room)

