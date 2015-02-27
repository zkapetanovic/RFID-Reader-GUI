#!/usr/bin/env python
"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovic
"""

import globals as tag
#from localThread import localThread
import sllurp.llrp as llrp
import numpy as np
import time

class UpdateTagReport:
	def parseData(self, epc, rssi, snr, time):
		tag.epc 			= epc	
		tag.tmp 			= "%02X" % int(epc[0:24], 16)
		tag.tagType 		= "%02X" % int(epc[0:2], 16)
		tag.hwVersion 		= "%02X" % int(epc[18:20], 16)
		tag.wispID 			= "%02X" % int(epc[0:2], 16)
		tag.snr 			= snr
		tag.rssi 			= rssi
		tag.time 			= time	#microseconds
	
		if tag.hwVersion is None:
			return

		#Store all tag IDs
		if tag.wispID not in tag.idEntry.keys():
			tag.idEntry[tag.wispID] = tag.newRow
			tag.newRow += 1
		'''
		log = [[tag.epc, tag.time]]	
		camLog = open('camLog.csv', 'w')
		for row in log:
			for column in row:
				camLog.write('%d ' % column)
			  	camLog.write('\n')
		camLog.close()
		'''
		#Accelerometer WISP
		if tag.tagType == "0B" or tag.tagType == "0D":
			if tag.tagType == "0B": alpha = 1.16
			else: alpha = 1

			self.accelerometer(alpha)

		#Temperature WISP
		elif tag.tagType == "0E" or tag.tagType == "0F": self.temperature()

		#Camera
		elif tag.tagType == "CA": 
			log = [[tag.epc, tag.time]]
			fileHandle = open('camLog.txt', 'a')
			np.savetxt(fileHandle, log, '%10s')
			fileHandle.close()
			self.imageCapture()

		#elif tag.tagType == "SOMETHING FOR LOCALIZATION":
		#	self.localization()

		#Unknown tag type
		else:
			#tag.sensorData = "N/A"
			#tag.camInfo = 0
			self.updateEntry()

	def accelerometer(self, alpha):
		percentage = alpha * 100 / 1024.
		xData = int(tag.epc[6:10], 16)
		yData = int(tag.epc[2:6], 16)
		zData = int(tag.epc[10:14], 16)
		tag.accelX = 100 - xData * percentage
		tag.accelY = 100 - yData * percentage
		tag.accelZ = zData * percentage
		tag.sensorData = '%6.2f%%, %6.2f%%, %6.2f%%' % (tag.accelX, tag.accelY, tag.accelZ)
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


	def imageCapture(self):
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

	
	def imageCaptureReadCMD(self):
		imageData = tag.readData[2:X]
 		begin 	= 4
 		end 	= 6
 		
		for x in range(30): #30 bytes of data
			tag.imArray[tag.index] = int(tag.readData[begin:end], 16)
			begin = end
			end = end + 2
			tag.index = tag.index + 1
		
		tag.wordPtr = tag.wordPtr + 16	

	def updateEntry(self):
		tag.entry = (tag.time, tag.wispID, tag.tagType, tag.tmp, tag.sensorData, tag.snr, tag.rssi)
		tag.entryCount += 1
		tag.data.append(tag.entry)








