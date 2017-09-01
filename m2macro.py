#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import zlib
import sys,traceback
import json
class Pointer:
	def __init__(self,dict):
		self.x=float(dict["AXIS_X"])
		self.y=float(dict["AXIS_Y"])
		self.id=int(dict["id"])
	def equals(self,p):
		return self.x==p.x and self.y==p.y

class Event:
	def __init__(self,dict):
		self.action=int(dict["action"])
		self.eventTime=int(dict["eventTime"])
		self.pointers=[]
		dpointers=dict["pointer"]
		self.activePointer=None
		i=0
		while True:
			si=str(i)
			if si in dpointers:
				p=Pointer(dpointers[si])
				self.pointers.append(p)
			else:
				break
			i+=1
	def down(self,pointer):
		if pointer:
			id=pointer.id
			if id>0:
				return "down#%d %.2f,%.2f"%(id,pointer.x,pointer.y)
			else:
				return "down %.2f,%.2f"%(pointer.x,pointer.y)
		else:
			print("down error:",self.eventTime)
			return None
	def up(self,pointer):
		if pointer:
			id=pointer.id
			if id>0:
				return "up#%d"%(id,)
			else:
				return "up"
		else:
			print("up error:",self.eventTime)
			return None
	def move(self,pointer):
		if pointer:
			id=pointer.id
			if id>0:
				return "move#%d %.2f,%.2f"%(id,pointer.x,pointer.y)
			else:
				return "move %.2f,%.2f"%(pointer.x,pointer.y)
		else:
			print("move error:",self.eventTime)
			return None

	def toString(self):
		fun={0:self.down,1:self.up,2:self.move,5:self.down,6:self.up}
		if not self.activePointer:
			if len(self.pointers)==1:
				self.activePointer=self.pointers[0]
			elif self.action!=2:
				activeid=0
				while self.action>256:
					activeid+=1
					self.action-=256
				for p in self.pointers:
					if p.id==activeid:
						self.activePointer=p
						break
			
		if self.action in fun:
			return fun.get(self.action)(self.activePointer)
		else:
			print("no fun",self.action,self.eventTime)
class Macro:
	def __init__(self,inputfile):
		self.macrostrings=[]
		
		filedata=self.readfile(inputfile)
		self.handledata(filedata)

	def addstring(self,s):
		self.macrostrings.append(s)

	def writeToFile(self,outputfile):
		with open(outputfile,"w") as outfile:
			for s in self.macrostrings:
				if s:
					outfile.write(s+"\n")

	def readfile(self,filename):
		with open(filename,"rb") as filein:
			filein.seek(0,2)
			filelength=filein.tell()
			filein.seek(0,0)
			filedata=filein.read(filelength)
			try:
				decodedata=zlib.decompress(filedata)
				filedata=decodedata
			except:
				pass
			
			return filedata.decode("utf-8")
	
	def handledata(self,filedata):
		pos=filedata.find('}{')
		if pos==-1:
			print("error data")
			sys.exit(1)
		headdata=filedata[:pos+1]
		bodydata=filedata[pos+1:]
		pos=bodydata.find('}{')
		if pos!=-1:
			bodydata=bodydata[:pos+1]
		jsonhead=None
		jsonbody=None
		try:
			jsonhead=json.loads(headdata)
			jsonbody=json.loads(bodydata)
		except Exception as e:
			print(traceback.format_exc())
			sys.exit(1)
		PackageName=jsonhead["PackageName"]
		Width,Height=jsonhead["Width"],jsonhead["Height"]
		self.addstring(PackageName)
		self.addstring("{} {}".format(Width,Height))
		self.StartTime=jsonhead["StartTime"]
		
		events=jsonbody["event"]
		
		eventslist=[]
		i=0
		while True:
			si=str(i)
			if si in events:
				e=Event(events[si])
				eventslist.append(e)
				if e.action==2 and len(e.pointers)>1:
					if i>1:
						e2=eventslist[i-1]
						for p1 in e.pointers:
							for p2 in e2.pointers:
								if p1.id==p2.id and not p1.equals(p2):
									e.activePointer=p1
									break
					
			else:
				break
			i+=1
		i=0
		lasttime=self.StartTime
		for e in eventslist:
			if e.eventTime>lasttime:
				self.addstring("delay %d"%(e.eventTime-lasttime))
			lasttime=e.eventTime
			self.addstring(e.toString())
			i+=1
		
if __name__=="__main__":
	if len(sys.argv)<3:
		print("usage: python3 m2macro.py [inputfile] [outputfile]")
		sys.exit(1)
	inputfile=sys.argv[1]
	outputfile=sys.argv[2]

	macro=Macro(inputfile)
	macro.writeToFile(outputfile)
