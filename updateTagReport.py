#!/usr/bin/env python
"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovice
"""

import globals as tag
#from localThread import localThread
import sllurp.llrp as llrp
import numpy as np
import time

class UpdateTagReport:
	def __init__(self):
		self.currentX, self.currentY, self.currentZ = 1, 1, 1
		self.xCorrect, self.yCorrect, self.zCorrect = 0.87, 0.886, 1.034
		
	def parseData(self, epc, rssi, snr, time, readData):
		tag.epc 			= epc	
		tag.tmp 			= "%02X" % int(epc[0:24], 16)
		tag.tagType 		= "%02X" % int(epc[0:2], 16)
		tag.hwVersion 		= "%02X" % int(epc[18:20], 16)
		tag.wispID 			= "%02X" % int(epc[0:2], 16)
		tag.snr 			= snr
		tag.rssi 			= rssi
		tag.time 			= time	#microseconds
		tag.readData		= readData
	
		if tag.hwVersion is None:
			return

		#Store all tag IDs
		if tag.wispID not in tag.idEntry.keys():
			tag.idEntry[tag.wispID] = tag.newRow
			tag.newRow += 1

		#Accelerometer WISP
		if tag.tagType == "0B" or tag.tagType == "0D":
			#if tag.tagType == "0B": alpha = 1.16
			#else: alpha = 1
			alpha = 0.9
			self.accelerometer(alpha)

		#Temperature WISP
		elif tag.tagType == "0E" or tag.tagType == "0F": self.temperature()

		#Camera
		elif tag.tagType == "CA": 
			#log = [[tag.epc, tag.time]]
			#fileHandle = open('camLog.txt', 'a')
			#np.savetxt(fileHandle, log, '%10s')
			#fileHandle.close()
			if tag.readData != 0:
				self.imageCaptureReadCMD() 
			else:
				print ("Update Entry")
				self.updateEntry()
		

		#elif tag.tagType == "SOMETHING FOR LOCALIZATION":
		#	self.localization()

		#Unknown tag type
		#else:
		#	tag.sensorData = "N/A"
			#tag.camInfo = 0
		#	self.updateEntry()


	def accelerometer(self, alpha):		
		x = int(tag.epc[6:10], 16)
		y = int(tag.epc[2:6], 16)
		z = int(tag.epc[10:14], 16)

		if x < 0 or x > 1024: x = 0
		if y < 0 or y > 1024: y = 0
		if z < 0 or z > 1024: z = 0

		x = 100.0 * x / 1024.0
		y = 100.0 * y / 1024.0
		z = 100.0 * z / 1024.0
		
		x = 100. - x
		y = 100. - y

		if tag.tagType == "0B":
			x = x * self.xCorrect;
			y = y * self.yCorrect;
			z = z * self.zCorrect;

		self.currentX = self.currentX * alpha + x * (1-alpha)
		self.currentY = self.currentY * alpha + y * (1-alpha)
		self.currentZ = self.currentZ * alpha + z * (1-alpha)
		
		tag.sensorData = '%6.2f%%, %6.2f%%, %6.2f%%' % (self.currentX, self.currentY, self.currentZ)
		tag.accelY, tag.accelX, tag.accelZ = self.currentY, self.currentX, self.currentZ

		if tag.saturnThread:
			tag.saturnThread.setAngles(self.currentX, self.currentY, self.currentZ)

		self.updateEntry()


	def temperature(self):
		tag.temp = int(tag.epc[2:6], 16)
		tempValue = ((tag.temp - 673) * 423.) / 1024.
		tag.sensorData = tempValue
		self.updateEntry()

	#def localization(self):
	#	self.lThread = localThread()
	#	self.lThread.daemon = True
	#	self.lThread.start()

	def imageCaptureReadCMD(self):
 		begin 	= 0
 		end 	= 2
 	
	 	if tag.index < 25200 and tag.wordPtr < 12600:
			for x in range(30): #32 bytes of data
				tag.imArray[tag.index] = int(tag.readData[begin:end], 16)
				begin = end
				end = end + 2
				tag.index = tag.index + 1
			
			tag.wordPtr = tag.wordPtr + 15
			print (tag.index)

		self.updateEntry()
			
	def imageCaptureEPC(self):
		tag.sensorData = int(tag.epc[2:24], 16)
		tag.prevSeq = tag.currSeq
		tag.currSeq = int(tag.epc[2:4], 16)
		tag.index = 10 * (200 * tag.sequence + tag.currSeq)

		#print tag.index, tag.sequence, tag.currSeq

		if tag.currSeq < tag.prevSeq: tag.sequence += 1

		if tag.currSeq != 255 or tag.index <= 25199:
			begin = 4
			end = 6
			for x in range(10):
				tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + x] = int(tag.epc[begin:end], 16)
				begin = end
				end = begin + 2

			if x == 9: x = 0

		######## Get missing data ########
		if tag.currSeq == 255:
			for i in range(len(tag.imArray)):
				if tag.imArray[i] == -1:
					tag.dataIndex.append(i) 					

			j = 0
			while j < len(tag.dataIndex):
				missingPacket = tag.dataIndex[j] / 10.
				tag.getPacket.append(missingPacket) 
				j = j + 10
			tag.retrieve = 1
			print (tag.retrieve)

		if tag.currSeq == 255 or tag.index >= 25199:
			tag.sequence, tag.currSeq, tag.prevSeq, tag.count = 0, 0, 0, 0
			return
	
		self.updateEntry()


	def updateEntry(self):
		tag.entry = (tag.time, tag.wispID, tag.tagType, tag.tmp, tag.sensorData, tag.snr, tag.rssi)
		tag.entryCount += 1
		tag.data.append(tag.entry)








