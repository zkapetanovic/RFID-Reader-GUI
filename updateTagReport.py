#!/usr/bin/env python


import globals as tag
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

		#Accelerometer WISP
		if tag.tagType == "0B" or tag.tagType == "0D":
			if tag.tagType == "0B": alpha = 1.16
			else: alpha = 1

			self.accelerometer(alpha)

		#Temperature WISP
		elif tag.tagType == "0E" or tag.tagType == "0F": self.temperature()

		#Camera
		elif tag.tagType == "CA": 
			self.imageCapture()

		#Unknown tag type
		else:
			tag.sensorData = "N/A"
			tag.camInfo = 0
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


	def imageCapture(self):
		tag.sensorData = int(tag.epc[2:24], 16)
		tag.prevSeq = tag.currSeq
		tag.currSeq = int(tag.epc[2:4], 16)
		tag.count = (200 * tag.sequence + tag.currSeq)

		print "count, sequence, 2byte"
		print tag.count, tag.sequence, tag.currSeq


		if tag.currSeq == 255 or tag.count >= 25400:
			tag.sequence 	= 0
			tag.currSeq 	= 0
			tag.prevSeq 	= 0
			tag.count 		= 0
			return

		if tag.currSeq < tag.prevSeq:
			tag.sequence += 1


		#tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + tag.dataCount] = int(tag.epc[tag.begin:tag.end])
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 0] = int(tag.epc[4:6], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 1] = int(tag.epc[6:8], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 2] = int(tag.epc[8:10], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 3] = int(tag.epc[10:12], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 4] = int(tag.epc[12:14], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 5] = int(tag.epc[14:16], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 6] = int(tag.epc[16:18], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 7] = int(tag.epc[18:20], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 8] = int(tag.epc[20:22], 16)
		tag.imArray[10 * (200 * tag.sequence + tag.currSeq) + 9] = int(tag.epc[22:24], 16)

		'''
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 0] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 1] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 2] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 3] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 4] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 5] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 6] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 7] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 8] = 1
		tag.boolPixelRecieved[10 * (200 * tag.sequence + tag.currSeq) + 9] = 1
		'''
		self.updateEntry()

	def updateEntry(self):
		tag.entry = (tag.time, tag.wispID, tag.tagType, tag.tmp, tag.sensorData, tag.snr, tag.rssi)
		tag.entryCount += 1
		tag.data.append(tag.entry)




		


