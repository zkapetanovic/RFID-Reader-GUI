# -*- coding= utf-8 -*-
"""
Created on Fri Jan 10 16=04=43 2014

@author: yizhao
@fun:	 1 Impinj reader configure parameter
         2 Update WISP Sense Data from EPC report
"""
import sllurp.llrp as llrp
import globals
from globals import*
import numpy as np
from collections import deque

#@todo: combine the EPC save all the tag state: powerUp, no detection, partial detection
# ping speedway reader to get the Code
# speedway 00-05-56 host = '128.95.28.173'
# speedway 00-05-EA host = ''169.254.128.56''
colorMap={'f0f0':color.yellow,'f0f1':color.blue,'f0f2':color.red,'f0f3':color.green}
tagSum ={'ID':'', 'readCtr':0,'validCtr':0,'powerUpCtr':0,'noTOACtr':0,'toaErr':0,
         'caliCtr':0,'color':(0,0,0),'mean':[0,0,0],'std':[0,0,0],'failCali': 0}

class readerConfig:
    def __init__(self,host = '169.254.128.56',  port = llrp.LLRP_PORT,
                 time = float(80),  debug = True,  every_n = 5, antennas = '1',
			tx_power = 61, modulation = 'WISP5',  tari= '0',
                 reconnect = True, logfile = 'logfile.log'):
        self.host       = host
        self.port       = port
        self.time       = time
        self.debug      = debug
        self.every_n    = every_n
        self.antennas   = antennas
        self.tx_power   = tx_power
        self.modulation = modulation
        self.tari       = tari
        self.reconnect  = reconnect
        self.logfile    = logfile
        globals.readSum['period'] = time
        		
class formatEPC:
	def __init__(self,tag,TagType=0,lTagType=2, EventCtr=2,lEventCtr=2, 
				 WispUS_ID=4,lWispUS_ID=4, DataAcc=8,DataTOA=16,DataSize=2,numTx=globals.numTx):
	     #format EPC data into tag data package
         self.tag ={'epc':tag['EPC-96'], 
					'ID': tag['EPC-96'][WispUS_ID:WispUS_ID+lWispUS_ID],
					'EventCtr':int(tag['EPC-96'][EventCtr:EventCtr+lEventCtr],16),
					'TOAs':[], 
					'ACCs':[],
					'rssi':tag['PeakRSSI'][0],
					'time':tag['LastSeenTimestampUTC'][0],#timeStamp in us (type is Long)
					'validCtr':0
					}
         #self.newFlg=0				
         for i in range (0,numTx):
             self.tag['TOAs'].append(int( \
             	tag['EPC-96'][DataTOA+i*DataSize:DataTOA+(i+1)*DataSize],16))
             if i:
                self.tag['TOAs'][i]= self.tag['TOAs'][i]+self.tag['TOAs'][i-1]
             #if i<3:
             self.tag['ACCs'].append(self.sign(int( \
                	tag['EPC-96'][DataAcc+i*DataSize:DataAcc+(i+1)*DataSize],16)))
             
         #print('acc',self.tag['ACCs'])     
         #reaself.tag['TOAs']=[112,207,293,390]   
         if self.newTag():
             #self.newFlg=1
             globals.log[self.tag['ID']]={}
             #print('new',self.newFlg)
             globals.log[self.tag['ID']]['logData']=[] 
             globals.log[self.tag['ID']]['xyz']=np.array([[0,0,0]])
             globals.log[self.tag['ID']]['sum']=tagSum.copy()
             globals.log[self.tag['ID']]['sum']['ID']=self.tag['ID']
             globals.log[self.tag['ID']]['sum']['color'] = colorMap[self.tag['ID']]
             globals.readSum['tagsID'].append(self.tag['ID']) 
         globals.log[self.tag['ID']]['sum']['readCtr'] +=1
         #print('inside',globals.log.keys())
         #print('sum',globals.log[self.tag['ID']]['sum'])  

	def sign(self,v):
         if not 0 <= v < 256: 
             raise ValueError, "hex number outside 16 bit range" 
         if v >= 128: 
             v = v - 256
         
         if v>=100:
             v=v-128
         elif v<=-100:
             v=v+128
         return v 
         
	def update(self):
		#global USTags
		#print('EPC',self.tag['epc'])
		#print('new update',self.newFlg)
		if self.validTOA():
			#print('TOA',self.tag['TOAs'])
			self.tag['validCtr'] = globals.log[self.tag['ID']]['sum']['validCtr']
			globals.log[self.tag['ID']]['sum']['validCtr'] +=1 
			#if self.tag['ID']=='f0f3':
				#self.motionUpdate()
				
			globals.readSum['allTag'] +=1
			#print('new',self.newFlg)
			if self.tag['ID'] not in globals.nowTags.keys():
				#print('saw new valid tag')
				#globals.log
				#['logData']: save all epc rssi time data 
				#['xyz']:save all ploted position data    note that xyz and logdata may have different length
				#[sum]: summary of all the result
				globals.nowTags[self.tag['ID']] = {'time':self.tag['time'],'TOAs':np.asarray(self.tag['TOAs'])} 
				globals.USTags[self.tag['ID']] = deque([self.tag])#create new valid tag que data package named by its 'US_ID'
			else:
				if self.tag['ID'] in globals.USTags.keys():#if the queue is not empty
					globals.USTags[self.tag['ID']].append(self.tag)
				else:
					globals.USTags[self.tag['ID']] = deque([self.tag])

			globals.log[self.tag['ID']]['logData'].append([self.tag['epc'],self.tag['rssi'],self.tag['time']]
					+self.tag['TOAs']+self.tag['ACCs'])
			return True             
		else:
			#print('WISP_US tag have no valid data')
			return False
			
			
	# def motionUpdate(self):
		# if self.ACCs[3]==64:
			# if(self.tag['ID'] not in motion.keys()):
				# motion[self.tag['ID']] = {}
				# motion[self.tag['ID']]['conCtr']=[1]
				# motion[self.tag['ID']]['list']=[globals.log[self.tag['ID']]['sum']['validCtr']]
				# motion[self.tag['ID']]['Flg']=1
			# else:
				# motion[self.tag['ID']]['conCtr']
					# ==(globals.log[self.tag['ID']]['sum']['validCtr']-1):					
				# motion[self.tag['ID']]['conCtr'] +=1
				# motion[self.tag['ID']]['currCtr']=globals.log[self.tag['ID']]['sum']['validCtr'] 
		# if not self.motion[3]==64:
				# motion[self.tag['ID']]['conCtr'] +=0
		
		
	def newTag(self):
		#global	USTags
		if self.tag['ID'] not in globals.log.keys():
			#self.newFlg = 1
			#print('new tag',self.newFlg)
			return True
		else:
			#self.newFlg = 0
			#print('not new')
			return False
	
	#updateTOA if TOA is valid
	def validTOA(self):
		#print(self.tag['TOAs'])
		if self.tag['TOAs'][0]==0xFF:
			globals.log[self.tag['ID']]['sum']['powerUpCtr'] +=1
		elif 0x00 in self.tag['TOAs'][0:3]:
			#print(self.tag['TOAs'])
			globals.log[self.tag['ID']]['sum']['noTOACtr'] +=1
		else:
			for i in self.tag['TOAs'][0:3]:
				if i<20 or i>65535:
					globals.log[self.tag['ID']]['sum']['toaErr'] +=1
					return False
					#return True
			return True 
		return False
		#return True
				
  
def updateWISP_US(tag):
    #print('get epc:')
    print(tag['EPC-96'])		
    #print(tag['EPC-96'])
    if ((tag['EPC-96'][0:2]) == 'b7'):
        #print(tag['EPC-96'])
        if formatEPC(tag).update():
            return True
    return False
		
		