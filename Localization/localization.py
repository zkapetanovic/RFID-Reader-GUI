#!/usr/bin/env python
"""
Created on Fri Jan 10 16=04=43 2014
@author: yizhao
"""

import globals
from globals import *

colorMap={'f0f0':color.yellow,'f0f1':color.blue,'f0f2':color.red,'f0f3':color.green}
tagSum ={'ID':'', 'readCtr':0,'validCtr':0,'powerUpCtr':0,'noTOACtr':0,'toaErr':0,
         'caliCtr':0,'color':(0,0,0),'mean':[0,0,0],'std':[0,0,0],'failCali': 0}


class Localization:
	def __init__(self,epc, TagType = 0, lTagType = 2, EventCtr = 2, lEventCtr = 2, WispUS_ID = 4,
				 lWispUS_ID = 4, DataAcc = 8, DataTOA = 16, DataSize = 2, numTx = globals.numTx):


		self.tag = {'epc' : epc,
					'ID' : epc[WispUS_ID:WispUS_ID + lWispUS_ID],
					'EventCtr' : int(epc[EventCtr:EventCtr+lEventCtr], 16),
					'TOAs': [],
					'ACCs': [],
					'rssi': tag.rssi,
					'time': tag.time,
					'validCtr': 0}

		for i in range(0, numTx):
			self.tag['TOAs'].append(int(tag['EPC-96'][DataTOA+(i*DataSize):DataTOA+((i+1)*DataSize)],16))

			if i:
				self.tag['TOAs'][i]= self.tag['TOAs'][i]+self.tag['TOAs'][i-1]
			#if i < 3:
			self.tag['ACCs'].append(self.sign(int(tag['EPC-96'][DataAcc+i*DataSize:DataAcc+(i+1)*DataSize],16)))

		if self.newTag():
			globals.log[self.tag['ID']] = {}
			globals.log[self.tag['ID']]['logData'] = [] 
			globals.log[self.tag['ID']]['xyz'] = np.array([[0,0,0]])
			globals.log[self.tag['ID']]['sum'] = tagSum.copy()
			globals.log[self.tag['ID']]['sum']['ID'] = self.tag['ID']
			globals.log[self.tag['ID']]['sum']['color'] = colorMap[self.tag['ID']]
			globals.readSum['tagsID'].append(self.tag['ID']) 
		globals.log[self.tag['ID']]['sum']['readCtr'] += 1
        

	def update(self):
		if self.validTOA():
			self.tag['validCtr'] = globals.log[self.tag['ID']]['sum']['validCtr']
			globals.log[self.tag['ID']]['sum']['validCtr'] += 1 
				
			globals.readSum['allTag'] += 1

			if self.tag['ID'] not in globals.nowTags.keys():
				globals.nowTags[self.tag['ID']] = {'time':self.tag['time'],'TOAs':np.asarray(self.tag['TOAs'])} 
				globals.USTags[self.tag['ID']] = deque([self.tag])		#Create a new valid tag que data package named by its 'US_ID'
			else:
				if self.tag['ID'] in globals.USTags.keys():				#if the queue is not empty
					globals.USTags[self.tag['ID']].append(self.tag)
				else:
					globals.USTags[self.tag['ID']] = deque([self.tag])

			globals.log[self.tag['ID']]['logData'].append([self.tag['epc'],self.tag['rssi'],self.tag['time']]
					+ self.tag['TOAs']+self.tag['ACCs'])
			return True
		else:
			return False

	def sign(self, v):
		if not 0 <= v < 256:
			raise ValueErrpr, "The hex number is outside of the 16-bit range"
		if v >= 128:
			v -= 256

		if v >= 100:
			v -= 128
		elif v <= -100:
			v += 128

		return v

	def newTag(self):
		if self.tag['ID'] not in globals.log.keys():
			return True
		else:
			return False


	def validTOA(self):
		if self.tag['TOAs'][0] == 0xFF:
			globals.log[self.tag['ID']]['sum']['powerUpCtr'] += 1
		elif 0x00 in self.tag['TOAs'][0:3]:
			globals.log[self.tag['ID']]['sum']['noTOACtr'] += 1
		else:
			for i in self.tag['TOAs'][0:3]:
				if i < 20 or i > 65535:
					globals.log[self.tag['ID']]['sum']['toaErr'] += 1
					return False
			return True 
		return False

