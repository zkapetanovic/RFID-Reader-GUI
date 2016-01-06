#!/usr/bin/env python
"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovice
"""

import sllurp.llrp as llrp
import numpy as np
import time
from skimage import exposure
import struct

class UpdateTagReport:
	def __init__(self, saturnThread, wispApp):
		#Entry
		self.idEntry 	  = {}
		self.entry        = ()
		self.data 	  = []
		self.entryCount	  = 0
		self.sensorData   = None
		self.newRow	  = 0

		#Accel
		self.currentX 	  = 1
		self.currentY 	  = 1
		self.currentZ 	  = 1
		self.flipX		  = 0
		self.flipY 		  = 0
		self.xcorr		  = 0.87
		self.ycorr		  = 0.886
		self.zcorr		  = 1.034

		#Tag Data
		self.time 		  = None
		self.tmp 		  = None
		self.tagType 	  = None 
		self.hwVersion 	  = None
		self.wispID 	  = None
		self.snr 		  = None
		self.rssi 		  = None
		self.readData 	  = None
		self.epc 		  = None

		#Temp
		self.tempValue	   = None
		self.plotData	   = []

		#WISPCam
		self.x 		   = 0
		self.y  	   = 50
		self.finished 	   = 0
		self.prevSeq 	   = 0 	
		self.sequence 	   = 0 			
		self.index 	   = 0
		self.retrieve 	   = 0
		self.readData 	   = 0
		self.wordPtr	   = 0
		self.mat_image 	   = None
		self.imageReady    = False
		self.imArray	   = [128 for x in range(25200)]
		self.missingPixels = []
		self.pixel 	   = 0

		#Threads
		self.saturnThread  = saturnThread
		self.wispApp 	   =  wispApp


	def getData(self, epc, rssi, snr, time):
		self.epc 		= epc	
		self.tmp 		= "%02X" % int(epc[0:24], 16)
		self.tagType 		= "%02X" % int(epc[0:2], 16)
		self.charge 		= "%02X" % int(epc[4:6], 16)
		self.hwVersion 		= "%02X" % int(epc[18:20], 16)
		self.wispID	 	= "%02X" % int(epc[0:2], 16)
		self.snr 		= snr
		self.rssi 		= rssi
		self.time 		= time	#microseconds

		if self.epc != None:
			self.parseData(self.tagType, self.hwVersion, self.wispID, self.epc)
		else:
			print ("Tag seen, no data recieved")

	def parseData(self, tagType, hwVersion, wispID, epc):

		if hwVersion is None:
			return

		#Store all tag IDs
		if wispID not in self.idEntry.keys():
			self.idEntry[wispID] = self.newRow
			self.newRow += 1

		#Accelerometer WISP
		if tagType == "0B" or tagType == "0D": 
			self.getAccel(epc, tagType)

		#Temperature WISP
		elif tagType == "0E" or tagType == "0F": 
			self.getTemp(epc, tagType)

		#WISPCam
		elif tagType == "CA": 
			#self.saveData()
			if int(self.epc[2:4], 16) != 254:
				self.imageCaptureEPC() 
			else:
				self.camCharge()

		else: 
			self.sensorData = None
			self.updateEntry()

	def saveImageData(self):
		log = [[self.epx, self.time]]
		fileHandle = open('camLog.txt', 'a')
		np.savetxt(fileHandle, log, '%10s')
		fileHandle.close()

	def getAccel(self, epc, tagType):
		alpha = 0.9

		x = int(epc[8:10], 16)
		y = int(epc[4:6], 16)
		z = int(epc[12:14], 16)

		if x < 0 or x > 1024: x = 0
		if y < 0 or y > 1024: y = 0
		if z < 0 or z > 1024: z = 0

		x = 100.0 * x / 1024.0
		y = 100.0 * y / 1024.0
		z = 100.0 * z / 1024.0

		self.accelerometer(alpha, x, y, z, tagType)

	def getTemp(self, epc, tagType):
		self.temp = int(tag.epc[2:6], 16)
		self.temperature(self.temp)

	def quickAccelCorrection(self, xcorr, ycorr, zcorr):
		self.xcorr, self.ycorr, self.zcorr = xcorr, ycorr, zcorr
		print str("New X correction factor: ") + str(self.xcorr)
		print str("New Y correction factor: ") + str(self.ycorr)
		print str("New Z correction factor: ") + str(self.zcorr)

	def accelerometer(self, alpha, x, y, z, tagType):	
		self.flipX, self.flipY = self.checkFlip()
		if self.flipX == 2:
			x = 100. - x
			self.flipX = 0

		if self.flipY == 2:
			y = 100. - y
			self.flipY = 0

		if tagType == "0B":
			x = x * self.xcorr
			y = y * self.ycorr
			z = z * self.zcorr

		self.currentX = self.currentX * alpha + x * (1 - alpha)
		self.currentY = self.currentY * alpha + y * (1 - alpha)
		self.currentZ = self.currentZ * alpha + z * (1 - alpha)
		
		self.sensorData = '%6.2f%%, %6.2f%%, %6.2f%%' % (self.currentX, self.currentY, self.currentZ)

		if self.saturnThread:
			self.saturnThread.setAngles(self.currentX, self.currentY, self.currentZ)

		self.updateEntry()

	def checkFlip(self):
		self.flipX = self.wispApp.xFlip.checkState()
		self.flipY = self.wispApp.yFlip.checkState()

		return self.flipX, self.flipY

	def temperature(self, temp):
		if temp < 0 or temp > 1024: temp = 0

		self.tempValue = ((temp - 673.) * 423.) / 1024.
		self.sensorData = self.tempValue
		self.plotData.append(self.tempValue)
		self.updateEntry()

	def updateAccel(self):
		return self.currentX, self.currentY, self.currentZ

	def updateTemp(self):
		return self.tagType, self.plotData	

	def imageCaptureEPC(self):
		self.wispApp.statusLabel.setText("<b>Status</b>: Transmitting")
		self.getCamProgress()
		self.sensorData = int(self.epc[2:24], 16)
		self.prevSeq = self.sequence
		self.finished = int(self.epc[2:4], 16)
		self.sequence = int(self.epc[2:6], 16)
		self.index = 9*self.sequence + 9

		#### Get missing pixels ####
		missing = self.sequence - self.prevSeq
		i = 1
		if missing >= 2:		
			while i < missing:
				p = self.prevSeq + i
				self.missingPixels.append(p)
				i += 1
			
		#### Append data to array ####
		if self.finished != 255 or self.index <= 25199:
			begin = 6
			end = 8
			for x in range(9):
				try:
					self.imArray[9*self.sequence + x] = int(self.epc[begin:end], 16)
					begin = end
					end = begin + 2
				except:
					print("Index error")
					self.index = 25200
					continue
			if x == 8: x = 0
		self.updateEntry()
		
		#### Did we get the last data set? ####
		if self.index % 175 == 0:
			self.configureImage(self.imArray)
			self.sequence, self.prevSeq, self.count = 0, 0, 0
			return

		if self.finished == 255 or self.index >= 25199:
			self.configureImage(self.imArray)
			self.sequence, self.prevSeq, self.count = 0, 0, 0
			return

	def imageFinished(self):
		if self.finished == 255 or self.index >= 25199:
			return True

	def getWriteData(self):
		self.missingPixels.append(10)
		if self.pixel < len(self.missingPixels):
			x = self.missingPixels[self.pixel]
			y = hex(x).split('x')[1]
			z = struct.pack('>I', x)
			if self.missingPixels[self.pixel] < 16:
				data = '\\' + 'x00' + '\\' + 'x0' + hex(x).split('x')[1]	
			elif self.missingPixels[self.pixel] >= 16 and x < 256:
				data = '\\' + 'x00' + '\\' + 'x' + hex(x).split('x')[1]
			elif self.missingPixels[self.pixel] >= 256 and x < 4096:
				data = '\\' + 'x0' + y[0] + '\\' + "x" + y[1:]
			elif self.missingPixels[self.pixel] >= 4096:
				data = '\\' + 'x' + y[0:2] + '\\' + 'x' + y[2:]
			self.pixel = self.pixel + 1
		print (data)
		return z

	def getCamProgress(self):
		x = int(self.epc[4:8],16)
		voltage = (x*4000)/1024;
		percentage = (((voltage*100)/3800)*100)/102;
		return percentage
		#self.wispApp.progress.setValue(percentage)
		#self.emit(QtCore.SIGNAL("updateProgressBar(int)"), percentage)
		#self.wispApp.progress.setValue(percentage)
		#self.wispApp.chargePercentage.setText(str(percentage) + "%")

	def configureImage(self, imArray):	
		rows, columns = 144, 175
		self.mat_image = np.reshape(imArray, (rows, columns)) / 255.0
		#self.mat_image = exposure.equalize_hist(self.mat_image)
		self.imageReady = True

	def updateImage(self):
		return self.mat_image, self.imageReady, self.index

	def updateTagReport(self):
		return self.tagType, self.wispID

	def updateEntry(self):
		self.entry = (self.time, self.wispID, self.tagType, self.tmp, self.sensorData, self.snr, self.rssi)
		self.data.append(self.entry)
		self.entryCount += 1
		return self.data, self.idEntry, self.newRow, self.entryCount
		
		
