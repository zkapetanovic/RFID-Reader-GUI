#!/usr/bin/env python

"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovic
"""

from PyQt4 import QtGui, Qt, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import numpy as np
import scipy
from scipy import ndimage

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys, threading, time, os
import pkg_resources

from GUI_Setup import GUI_Setup
from inventory import Reader
from updateTagReport import UpdateTagReport
from saturn import SaturnDemo
import globals as tag


class RFID_Reader_App:
	def __init__(self):

		self.impinjThread = Reader()
		self.saturnThread = SaturnDemo()
		self.usrpStart = False
		self.impinjStart = False

		self.runStarted = 0
		self.pause = 0

		wispApp.startButton.clicked.connect(self.start)
		wispApp.stopButton.clicked.connect(self.stop)
		wispApp.connectButton.clicked.connect(self.readerSelect)
		wispApp.saturnButton.clicked.connect(self.initSaturn)
		wispApp.captureButton.clicked.connect(self.captureImage)
		wispApp.pauseButton.clicked.connect(self.pauseRun)
		wispApp.clearButton.clicked.connect(self.clearImage)


	def readerSelect(self):
		if wispApp.impinjSelect.isChecked() == True:
			self.impinjStart = True
			tag.host = str("%s" % wispApp.ipAddress.toPlainText())
			print tag.host
		elif wispApp.usrpSelect.isChecked() == True:
			self.usrpStart = True


	def start(self):
		if self.runStarted == 0:
			self.runStarted = 1
			self.timer = QtCore.QTimer()
			self.timer.timeout.connect(self.updateGUI)
			self.timer.timeout.connect(self.captureImage)
			self.timer.timeout.connect(self.updateTemp)
			self.timer.timeout.connect(self.updateAccel)
			self.timer.start(50)
			self.initReader()

		if self.pause == 1:
			self.impinjThread.factory.resumeInventory()
			self.pause = 0


	def stop(self):
		self.impinjThread.impinj.stop()
		self.timer.stop()


	def pauseRun(self):
		self.impinjThread.factory.pauseInventory()
		self.pause = 1

	def clearTable(self):
		tag.data = []
		tag.idEntry = []
		tag.newRow = 0
		tag.entryCount = 0
		wispApp.mainTable.clearContents()		


	def initReader(self):
		if self.impinjStart == True:

			self.impinjThread.daemon = True
			wispApp.statusLabel.setText("<b>Status</b>: Charging")
			self.impinjThread.start()

		elif self.usrpStart == True:
			global usrp_tb
			self.usrp_tb = my_top_block()
			self.usrp_tb.start()


	def initSaturn(self):
		#self.saturnThread = SaturnDemo()
		self.saturnThread.daemon = True
		self.saturnThread.start()
		tag.saturn = True

	def initLocalization(self):
		self.plottingThread = LocalizationPlotting()
		self.plottingThread.daemon = True
		self.plottingThread.start()


	############### Update GUI ##############
	def updateGUI(self):
		lastRow = wispApp.mainTable.rowCount()
		wispApp.mainTable.setRowCount(tag.newRow)
		wispApp.mainTable.resizeColumnsToContents()
		wispApp.mainTable.horizontalHeader().setStretchLastSection(True)
		
		if tag.tagType != "CA":
			wispApp.statusLabel.setText("<b>Status</b>: Charging")

		for fieldPos in range(7):
			currentValue = tag.idEntry.get(tag.wispID)
			values = tag.idEntry.values()

			if currentValue in values:
				item = QtGui.QTableWidgetItem(str(tag.data[tag.entryCount - 1][fieldPos]))
				wispApp.mainTable.setItem(currentValue, fieldPos, item)
		
	
	def updateTemp(self):
		if tag.tagType == "0F" or tag.tagType == "0E":
			plt.clf()
			plt.grid(True)
			tag.plotData.append(tag.sensorData)
			axes = wispApp.figure.add_subplot(111)
			axes.plot(tag.plotData, color = 'red')
			plt.title('Temperature', fontsize = 12)
			plt.ylim(-100, 100)
			wispApp.canvas.draw()


	def updateAccel(self):
		if tag.tagType == "0B" or tag.tagType == "0D":

			if tag.saturn == True:
				self.saturnThread.setAngles(tag.accelX, tag.accelY, tag.accelZ)

			wispApp.xAccel.setText(" X '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelX)
			wispApp.yAccel.setText(" Y '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelY)
			wispApp.zAccel.setText(" Z '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelZ)

			wispApp.sliderY.setValue(tag.accelY)
			wispApp.sliderX.setValue(tag.accelX)
			wispApp.sliderZ.setValue(tag.accelZ)


	def captureImage(self):
		if tag.tagType == "CA":
			wispApp.statusLabel.setText("<b>Status</b>: Transmitting data")
			rows 	= 144
			columns = 175

			tag.x = str("%s" % wispApp.xVal.toPlainText())
			tag.y = str("%s" % wispApp.xVal.toPlainText())
			
			if tag.count >= 25199 or int(tag.epc[2:4], 16) == 255:
				if tag.saved == 0:
					tag.saved = 1
					print int(tag.epc[2:4], 16)
					wispApp.statusLabel.setText("Status: Image captured")

					for i in tag.imArray:
						if i <= tag.x: 	i = 0
						elif i > tag.y: i = 255
					
					plt.cla()															#clear plot
					plt.clf()															#clear plot			
					matrix = np.reshape(tag.imArray, (rows, columns)) / 255.0 		#create matrix
					mat_image = ndimage.rotate(matrix, 270)
					plt.gray()															#set to grayscale
					self.image = wispApp.image.add_subplot(111) 						#create subplot
					self.image.clear()													#clear previous image
					self.ax = wispApp.image.gca() 										#remove axis
					self.ax.set_axis_off()												#remove axis
					self.image.imshow(mat_image, aspect='auto')										#display image
					wispApp.imageCanvas.draw()											#display image
					
					name = 'ImageLog/imagelog' + str(tag.fileCount)
					fileHandle = open(name, 'a')
					np.savetxt(fileHandle, tag.imArray, '%10s')
					fileHandle.close()
					tag.fileCount += 1
					print name
					tag.imArray = [128 for z in range(25200)]	


	def clearImage(self):
		plt.cla()																	#clear plot
		plt.clf()																	#clear plot
		self.image.clear()															#clear previous image
		self.ax.set_axis_off()														#remove axis
		tag.imArray = [128 for z in range(25200)]									#reset array

		print ("Image Capture Cleared")



def main():
	app = QtGui.QApplication(sys.argv)
	global wispApp 
	wispApp = GUI_Setup()
	demo = RFID_Reader_App()
	wispApp.setWindowTitle("WISP Demo")
	sys.exit(app.exec_())

if __name__ == '__main__': main()
		