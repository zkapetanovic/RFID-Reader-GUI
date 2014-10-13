#!/usr/bin/env python

from localization import Localization
import globals as tag


class UpdateTagReport:
	def parseData(self, epc, rssi, snr, time):
		tag.epc 			= epc	
		tag.tmp 			= "%02X" % int(epc[0:24], 16)
		tag.tagType 		= "%02X" % int(epc[0:2], 16)
		tag.hwVersion 		= "%02X" % int(epc[18:20], 16)
		tag.wispID 			= "%02X" % int(epc[22:24], 16)
		tag.snr 			= snr
		tag.rssi 			= rssi
		tag.time 			= time	#microseconds


	
		if tag.hwVersion is None:
			return

		#Store all tag IDs
		if tag.wispID not in tag.idEntry.keys() and tag.tagType != "CA":
			tag.idEntry[tag.wispID] = tag.newRow
			tag.newRow += 1

		#Accelerometer WISP
		if tag.tagType == "0B" or tag.tagType == "0D":
			if tag.tagType == "0B": alpha = 1.16
			else: alpha = 1

			self.accelerometer(alpha)

		#Temperature WISP
		elif tag.tagType == "0E" or tag.tagType == "0F": self.temperature()
		#Localization
		elif tag.tagType == "B7": 
			if tag.wispID not in tag.lTags.keys():
				tag.lTags[tag.wispID] = tag.lnewRow
				tag.lnewRow += 1
			self.localization()

		#Camera
		elif tag.tagType == "CA": 
			tag.capturing = 1
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
		print xData, yData, zData
		tag.accelX = 100 - xData * percentage
		tag.accelY = 100 - yData * percentage
		tag.accelZ = zData * percentage
		print tag.accelX, tag.accelY, tag.accelZ
		tag.sensorData = '%6.2f%%, %6.2f%%, %6.2f%%' % (tag.accelX, tag.accelY, tag.accelZ)
		print "accelerometer"
		print tag.sensorData
		self.updateEntry()


	def temperature(self):
		tag.temp = int(tag.epc[2:6], 16)
		print tag.temp
		tempValue = ((tag.temp - 673) * 423.) / 1024.
		print "temp"
		print tempValue
		tag.sensorData = tempValue
		self.updateEntry()


	def localization(self):
		tag.entry = (tag.time, tag.wispID, tag.tagType, tag.tmp, tag.sensorData, tag.snr, tag.rssi)
		tag.entryCount += 1
		tag.lData.append(tag.entry)


	def imageCapture(self):
		tag.prevSeq = tag.currSeq
		tag.currSeq = int(tag.epc[2:4], 16)
		tag.count += 1

		if tag.currSeq == 255 or tag.count >= 2500:
			tag.sequence 	= 0
			tag.currSeq 	= 0
			tag.prevSeq 	= 0
			tag.count 		= 0
			return

		if tag.currSeq < tag.prevSeq:
			tag.sequence += 1
		print "count, sequence"
		print tag.count, tag.sequence

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


	def updateEntry(self):
		tag.entry = (tag.time, tag.wispID, tag.tagType, tag.tmp, tag.sensorData, tag.snr, tag.rssi)
		tag.entryCount += 1
		tag.data.append(tag.entry)




		


