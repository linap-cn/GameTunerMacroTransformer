import zlib
import sys,time
import json
from collections import Iterable
import copy

PackageVersion="1.0.0"
StartTime=100000
HeaderVersion="1.0"
PIECETIME=20

class Pointer:
	def __init__(self,id):
		self.id=id
		self.x=0
		self.y=0
		self.data={}
		self.data["AXIS_PRESSURE"]=1
		self.data["AXIS_SIZE"]=0.025
		self.data["ORIENTATION"]=0
		self.data["TOOL_MAJOR"]=0
		self.data["TOOL_MINOR"]=0
		self.data["TOUCH_MAJOR"]=0
		self.data["TOUCH_MINOR"]=0
		self.data["toolType"]=1
	def toDict(self):
		self.data["AXIS_X"]=self.x
		self.data["AXIS_Y"]=self.y
		self.data["id"]=self.id
		return self.data
		
	def move(self,x,y):
		self.x=x
		self.y=y

class Event:
	LastTime=StartTime
	DownTime=StartTime
	Pointers=[]
	def __init__(self):
		self.eventpts=copy.deepcopy(Event.Pointers)
		self.data={}
		self.action=0
		self.data["actionButton"]=0
		self.data["buttonState"]=0
		self.data["deviceId"]=10
		self.data["edgeFlags"]=0
		self.data["flags"]=0
		self.data["metaState"]=0
		self.data["source"]=4098
		self.data["xPrecision"]=1.3333333730697632
		self.data["yPrecision"]=1.3333333730697632
		self.eventTime=StartTime

	def toDict(self):
		self.data["action"]=self.action
		i=0
		pointer={}
		self.data["pointer"]=pointer
		for pt in self.eventpts:
			pointer[str(i)]=pt.toDict()
			i+=1
		self.data["downTime"]=Event.DownTime
		self.data["eventTime"]=self.eventTime
		return self.data

	def settime(self,eventtime):
		self.eventTime=eventtime
	
	def down(self,id,arg):
		if len(self.eventpts)==0:
			self.action=0
		else:
			self.action=id*256+5
		xy=arg.split(',')
		pt=Pointer(id)
		pt.move(float(xy[0]),float(xy[1]))
		self.eventpts.append(pt)
		Event.Pointers.append(pt)
		return self

	def up(self,id,arg):
		if len(self.eventpts)<=1:
			self.action=1
		else:
			if id==0:
				self.action=6
			else:
				self.action=id*256+6
		for p in Event.Pointers:
			if p.id==id:
				Event.Pointers.remove(p)
				break
		return self

	def move(self,id,arg):
		self.action=2
		for pt in self.eventpts:
			if pt.id==id:
				xy=arg.split(',')
				if len(xy)==2:
					pt.move(float(xy[0]),float(xy[1]))
				else:
					evlist=[]
					expiretime=int(xy[2])
					n=expiretime/PIECETIME
					x=float(xy[0])
					y=float(xy[1])
					dx=(x-pt.x)/n
					dy=(y-pt.y)/n
					for i in range(0,int(n)):
						ev=Event()
						ev.settime(self.eventTime+PIECETIME*i)
						ev.move(id,("%f,%f")%(pt.x+dx*(i+1),pt.y+dy*(i+1)))
						evlist.append(ev)
					pt.move(float(xy[0]),float(xy[1]))
					self.settime(self.eventTime+expiretime)
					Event.LastTime+=expiretime
					evlist.append(self)
					return evlist
				break
		return self

	def tap(self,id,arg):
		self.down(id,arg)
		newev=Event()
		newev.up(id,arg)
		newev.settime(self.eventTime+1)
		return self,newev

	def delay(self,id,arg):
		Event.LastTime+=int(arg)
		return None

	def parse(self,op,id,arg):
		if not self.eventpts:
			Event.DownTime=Event.LastTime
		operator = {'down':self.down,'up':self.up,'move':self.move,'tap':self.tap,'delay':self.delay}
		if op in operator:
			self.settime(Event.LastTime)
			print(op,id,arg)
			return operator.get(op)(id,arg)
		else:
			return None

class Macro:
	def __init__(self,inputfile):
		self.events=[]
		jsonhead={}
		jsonhead["PackageVersion"]=PackageVersion
		jsonhead["StartTime"]=StartTime
		jsonhead["HeaderVersion"]=HeaderVersion
		self.jsonhead=jsonhead
		self.jsonevents={}
		self.jsonbody={"event":self.jsonevents}
		
		self.readfile(inputfile)

	def toBytes(self):
		i=0
		for ev in self.events:
			self.jsonevents[str(i)]=ev.toDict()
			i+=1
		jsonheaddata=json.dumps(self.jsonhead,indent=4,sort_keys=True)
		jsonbodydata=json.dumps(self.jsonbody,indent=4,sort_keys=True)
		return (jsonheaddata+jsonbodydata).encode("utf-8")
	
	def writeToFile(self,outputfile):
		with open(outputfile,"wb") as outfile:
			outfile.write(zlib.compress(self.toBytes()))
			#outfile.write(self.toBytes())

	def readfile(self,filename):
		with open(filename,"r") as filein:
			for line in filein:
				line=line.strip()
				if line:
					if not "PackageName" in self.jsonhead:
						self.jsonhead["PackageName"]=line
					elif not "Width" in self.jsonhead:
						wh=line.split(' ')
						Width=int(wh[0])
						Height=int(wh[1])
						self.jsonhead["Width"]=Width
						self.jsonhead["Height"]=Height
					else:
						self.parseline(line)

	def parseline(self,str):	
		ops=str.split(' ')
		evs=None
		op=ops[0]
		id=0
		if '#' in op:
			pos=op.find('#')
			id=int(op[pos+1:])
			op=op[:pos]
		if len(ops)>1:
			evs=Event().parse(op,id,ops[1])
		else:
			evs=Event().parse(op,id,None)
		if evs:
			if isinstance(evs, Iterable):
				self.events.extend(evs)
			else:
				self.events.append(evs)

if __name__=="__main__":
	if len(sys.argv)<3:
		print("usage: python3 macro2m.py [inputfile] [outputfile]")
		sys.exit(1)
	inputfile=sys.argv[1]
	outputfile=sys.argv[2]

	macro=Macro(inputfile)
	macro.writeToFile(outputfile)
