#!/usr/bin/env python

"""
Created on Fri Jan 10 14:50:05 2014
@author: yizhao
"""
import csv
from collections import namedtuple
from operator import itemgetter

import cv2.cv as cv
import cv2

import threading
import numpy as np
import random

import sllurp.llrp as llrp

from triCal import *
from cam import *
from plot3D import *
import globals

class localThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.cam 	= 0;
		self.Win3D 	= 1;
		
	def run(self):
		self.showTag()

		for tag in globals.idEntry.keys():
			self.logTest(globals.logName, tag)
			print(globals.log[tag]['sum'])

		print('fname',globals.logName)
		print('readSum',globals.readSum)
		print('detect pouring count',globals.pourCtr)


	def showTag(self):
		global win
		win  = plot3D()
		if(any(globals.USTags)):
			for tag in globals.USTags.keys():
				if (globals.USTags[tag]):
					plotTag=globals.USTags[tag].popleft()                    
					if self.isMove(plotTag):
						print('Tag is moving, reset xyz buffer and plot new data until movement is finish')
						alpha = 0x0   
					else:
						alpha = self.time_weight(plotTag['time'],plotTag['ID'])
						#alpha=0x0
					#filter TOA should we filter it now?
					oldTOA = globals.nowTags[plotTag['ID']]['TOAs']	
					globals.nowTags[plotTag['ID']]['TOAs'] = self.smooth(plotTag['TOAs'],oldTOA,alpha) 
					
					newXYZ = caliXYZ(plotTag['TOAs'],4).T
					#newXYZ=caliXYZ(globals.nowTags[plotTag['ID']]['TOAs'],3).T
					#print('newXYZ',newXYZ)
					#newXYZ=np.array([pairSelect(globals.nowTags[plotTag['ID']]['TOAs'],rOpt='r*p',numTx=4)])
					if(not newXYZ.any()):
						globals.log[plotTag['ID']]['sum']['failCali'] += 1
						continue
					self.filterXYZ(newXYZ,plotTag['ID'],alpha)
					location = globals.nowTags[plotTag['ID']]['xyz']
					#self.isPouring(plotTag)
					if self.cam == 1:                      
						self.tagToCam(location)
					if self.Win3D == 1:
						if(location.any()):
							#log current location
							globals.log[plotTag['ID']]['logData'][plotTag['validCtr']].extend(location[0])
							self.isPouring(plotTag)
							#print('logData')
							#print(globals.log[plotTag['ID']]['logData'])
							#print(location)
							#update current location result
							self.tag3D(location,plotTag['ID'])
							globals.log[plotTag['ID']]['xyz'] = np.r_[globals.log[plotTag['ID']]['xyz'],location]
							if not ((globals.log[plotTag['ID']]['xyz'][0]).any()):
								globals.log[plotTag['ID']]['xyz'] = np.delete(globals.log[plotTag['ID']]['xyz'],(0),axis=0)
		return
                          #print('here')

	def tag3D(self, xyz, ID, mode = 'static', colorAdd = (0, 0, 0)):
		#print('mode is',mode,'location',location,'any',any(location))
		if mode=='static':
			#print('xyz',xyz,'ID',ID)
			colors=tuple(map(sum,zip(globals.log[ID]['sum']['color'],colorAdd)))
			points(pos=xyz,size=5,color=colors)
			#print('plot TOA',xyz)
			#globals.win.blueDot.pos=np.r_[globals.win.blueDot.pos,Blue]
			#globals.tagSum['tagPlotBlue'] =  globals.tagSum['tagPlotBlue']+1
		elif mode=='dynamic':
			#globals.blue=np.r_[globals.blue,Blue]
			#globals.red=np.r_[globals.red,Red]
			#globals.tagSum['tagPlotBlue'] =  globals.tagSum['tagPlotBlue']+1
			#print('refore',Blue,'After',Red)
			globals.win.redBall.pos=xyz[0]
		else:
			print('mode is error')


	def tagToCam(localization):
		#tag=tag[0]
		#location = caliXYZ4(tag['DataTOA'],numTx=4)
		location = np.asarray([location],dtype=np.float32)*10
		if location.any():
			#cm = 10mm
			#print("location")
			globals.myCam.tagPosition = location
			globals.myCam.tagPosition[0][1]=288-globals.myCam.tagPosition[0][1]
			globals.myCam.tagPosition[0][2]=globals.myCam.tagPosition[0][2]
			globals.tagCtr=globals.tagCtr+1 
			globals.myCam.updateCam("trackTag")        
			#globals.myCam.updateCam("trackTagAndCircle")
		#else:
			#print('error caliXYZ ')
		#return location


	################################### FILTER ###################################	
	#Smooth alpha should be based on time difference
	#The longer the delay is, the larger on current data
	def time_weight(self,time,ID):
		dT  = time-globals.nowTags[ID]['time']
		globals.nowTags[ID]['dT'] = dT
		#print('DT',dT)
		#print('time',time,'globals.nowTags',globals.nowTags[ID]['time'],'dT',dT)
		history = 90000.000 # the larger history the more weight on history
		if(dT < 0):
			dT = -1*dT
		alpha = history/(dT+history) # min dT is 24, so max alpha is 0.67 
		assert 0 <= alpha <= 1
		#if not(0 <= alpha <= 1):
			 #alpha = 1;
			 #print('alpha',alpha,'DT',dT)
		#print('alpha',alpha)
		globals.nowTags[ID]['time']=time
		return alpha


	def smooth(self,new,old,alpha):
		new = np.asarray(new)
		"""Perform exponential smoothing with factor `alpha`=history weight."""
		#print('old',old)
		#print ((1-alpha)*new)
		#print((alpha*old))
		return ((1-alpha)*new+alpha*old)


	def filterXYZ(self,newXYZ,ID,alpha):  
		if 'xyz' not in globals.nowTags[ID]: #or alpha ==0x0  (globals.activeFlg>0 and ID=='f0f3'):
			#plot('inital TOAs',plot['TOAs'])
			globals.nowTags[ID]['xyz'] = newXYZ	
			#print('newXYZ',newXYZ)
			#globals.nowTags[ID]['eXYZ'] = newXYZ
			globals.nowTags[ID]['p']	= 0.7
			return 
		if	(globals.activeFlg>0) and (ID=='f0f3'):
			alpha=0
		# adding noise std
		p = globals.nowTags[ID]['p'] + 2.5
		k = p/(p+alpha/1.7)
		globals.nowTags[ID]['xyz'] += k*(newXYZ-globals.nowTags[ID]['xyz'])
		globals.nowTags[ID]['p'] = (1-k)*p	
		#print('newXYZ',newXYZ,'old',globals.nowTags[ID]['xyz'])
		if not self.isErr(ID,newXYZ):
			globals.nowTags[ID]['xyz'] = np.asarray([self.smooth(newXYZ[0],globals.nowTags[ID]['xyz'][0],alpha)])
	  #IQData = namedtuple("IQData", "date iq")     
	  
	  
	 # def filterXYZ(self,newXYZ,ID,alpha):                      
		# if 'xyz' not in globals.nowTags[ID]:
			# #plot('inital TOAs',plot['TOAs'])
			# globals.nowTags[ID]['xyz'] = newXYZ
			# return 
		# if not self.correctErr(ID,newXYZ):
			# globals.nowTags[ID]['xyz'] = np.asarray([self.smooth(newXYZ[0],globals.nowTags[ID]['xyz'][0],alpha)])
	  # #IQData = namedtuple("IQData", "date iq")     
	  

	def isShaking(self):
		return True


	def isMove(self,tag):
		#print(tag['ACCs'])
		if(tag['ACCs'][3]&0x40 and tag['ID'] == 'f0f3'):
			#
			globals.activeFlg = 5# put a threshold here, wait for 6 data after activeFlg detected in order to refer inability
			return True
		if(tag['ACCs'][3] == 0x1 and globals.activeFlg > 0 and tag['ID'] == 'f0f3'):
			globals.activeFlg -= 1
		return False


	def isTurn(self,tag):
		if (tag['ACCs'][3] == 0):
			return False
		#print(tag['ACCs'])	
        #if(tag['ACCs'][0])<48 and abs(tag['ACCs'][1])>50:
		if(tag['ACCs'][0] > 0) and (tag['ACCs'][1] <- 20 or tag['ACCs'][1] > (-5)):
			globals.log[tag['ID']]['logData'][tag['validCtr']].extend(['is turn'])
			print('is turning into Horizontal')
			return True
		if globals.activeFlg > 0:
			globals.log[tag['ID']]['logData'][tag['validCtr']].extend(['in action'])
		return False


	def isPouring(self,tag):
		#print('check')
		if (globals.activeFlg < 1):
			return False
		if self.isTurn(tag):
			d = {}
			#globals.activeFlg +=1
			#others={'red':np.asarray([[1.65,-7.2,66.36]]),'yellow':np.asarray([[27.05,-7.2,66.36]])}
			others = {'red':np.asarray([[1.65,-7.2,53.66]]),'yellow':np.asarray([[27.05,-7.2,53.66]])}
			#others={'red':np.asarray([[1.65,-7.2,66.36]]),'yellow':np.asarray([[27.05,-7.2,66.36]])}
			for otherTag in others.keys():
				#if not otherTag == tag['ID']:
					#print('other xyz',globals.nowTags[otherTag['ID']]['xyz'])
				thisTagL = mean(globals.log[tag['ID']]['xyz'][-4:],axis=0)
				d[otherTag]=np.linalg.norm(others[otherTag]-thisTagL)
			globals.pourCtr += 1
			print('d',d)
			print(tag['ID'] + ' is pouring into '+min(d,key=d.get))
			globals.log[tag['ID']]['logData'][tag['validCtr']].extend([tag['ID'] + ' is pouring into ' + min(d,key = d.get)])
			return True
		return False


	def isMoving(self):
		return True


	def isErr(self, ID, newXYZ):
		if len(globals.log[ID]['xyz']) > 6:
			dp=(globals.nowTags[ID]['dT'] / 6000)#practical movement distance given those time
			d=np.linalg.norm(globals.nowTags[ID]['xyz']-newXYZ)#actually movement distance now
			if dp < d:
				print('detection error')
				globals.nowTags[ID]['xyz'] = np.asarray([np.mean(globals.log[ID]['xyz'][-10:],axis = 0)])#+dp/(dp+d)
				return True
		return False


	################################### DATA LOG FUNCTION ###################################
	def logTest(self,fname,ID):
		#print('unplot',len(globals.USTags))
		if len(globals.log[ID]['xyz']):	
			globals.log[ID]['sum']['mean']=np.mean(globals.log[ID]['xyz'],axis=0)
			globals.log[ID]['sum']['std']=np.std(globals.log[ID]['xyz'],axis=0)
			"""
			ellipsoid(pos=globals.log[ID]['sum']['mean'],length=globals.log[ID]['sum']['std'][0],
					  height=globals.log[ID]['sum']['std'][1], width=globals.log[ID]['sum']['std'][2],
					  color=globals.log[ID]['sum']['color'])
			"""
			if globals.log[ID]['sum']['validCtr']>0:
				self.save(fname+'_'+ID,globals.log[ID]['logData'])
				self.save('xyz_'+fname+'_'+ID,globals.log[ID]['xyz'])
				self.save('sum_'+fname+'_'+ID,globals.log[ID]['sum'])


	################################### SAVE LIST INTO CSV ###################################
	def save(self,name,obj):
		print("save file")
		fname=str('./line_fit/'+name)+'.csv'
		with open(fname, 'wb') as csvfile:      
			if (type(obj)==type([])) or (type(obj)==type(np.asarray([]))):
				writer = csv.writer(csvfile)
				for value in obj:
					writer.writerow(value)
			elif type(obj)==type({}):
				writer = csv.DictWriter(csvfile,obj.keys())
				writer.writeheader()
				writer.writerow(obj)
			else:
				writer.writerow(obj) 