#!/usr/bin/env python

"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovic
"""

from PyQt4 import QtGui, Qt, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import numpy as np
import pyqtgraph as pg

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys, threading, time
import pkg_resources

from GUI_Setup import GUI_Setup
from inventory3 import Reader
from updateTagReport import UpdateTagReport
from localizationPlotting import LocalizationPlotting
from saturn import SaturnDemo

import globals as tag


class RFID_Reader_App:
	def __init__(self):
		self.usrpStart = False
		self.impinjStart = False
		self.runStarted = False

		wispApp.startButton.clicked.connect(self.start)
		wispApp.stopButton.clicked.connect(self.stop)
		wispApp.connectButton.clicked.connect(self.readerSelect)
		wispApp.saturnButton.clicked.connect(self.initSaturn)
		wispApp.local3DButton.clicked.connect(self.initLocalization)
		wispApp.captureButton.clicked.connect(self.captureImage)


	def readerSelect(self):
		if wispApp.impinjSelect.isChecked() == True:
			self.impinjStart = True
			tag.host = str("%s" % wispApp.ipAddress.toPlainText())
			print tag.host
		elif wispApp.usrpSelect.isChecked() == True:
			self.usrpStart = True


	def start(self):
		self.runStarted = True
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateGUI)
		self.timer.timeout.connect(self.captureImage)
		self.timer.timeout.connect(self.updateTemp)
		self.timer.timeout.connect(self.updateAccel)
		self.timer.start(100)
		self.initReader()


	def stop(self):
		self.impinjThread.impinj.stop()
		self.timer.stop()


	def initReader(self):
		if self.impinjStart == True:
			global impinjThread
			self.impinjThread = Reader()
			self.impinjThread.daemon = True
			self.impinjThread.start()
		elif self.usrpStart == True:
			global usrp_tb
			self.usrp_tb = my_top_block()
			self.usrp_tb.start()


	def initSaturn(self):
		self.saturnThread = SaturnDemo()
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
			wispApp.xAccel.setText(" X '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelX)
			wispApp.yAccel.setText(" Y '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelY)
			wispApp.zAccel.setText(" Z '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelZ)

			wispApp.sliderY.setValue(tag.accelY)
			wispApp.sliderX.setValue(tag.accelX)
			wispApp.sliderZ.setValue(tag.accelZ)

			if tag.saturn == True:
				self.saturnThread.setAngles(tag.accelX, tag.accelY, tag.accelZ)


	def captureImage(self):
		if tag.tagType == "CA":
			rows 	= 144
			columns = 175

			#tag.x = str("%s" % wispApp.xVal.toPlainText())
			#tag.y = str("%s" % wispApp.xVal.toPlainText())
			tag.x = 0
			tag.y = 20
			if int(tag.tmp[2:4], 16) == 255:
				#print "capture image"		
				#camera_image = np.loadtxt(r'CAMERA.txt')
				#raw_image = camera_image[0:25200]
			
				for i in tag.imArray:
					if i <= tag.x: 	i = 0
					elif i > tag.y: i = 255



				mat_image = np.reshape(tag.imArray, (rows, columns)) / 255.0
				#print mat_image
				plt.gray()
				image = wispApp.image.add_subplot(111)
				image.clear()
				image.imshow(mat_image)
				wispApp.imageCanvas.draw()

				time.sleep(5)
				tag.imArray	= [128 for x in range(25200)]
				image.clear()
				#tag.sequence = 0
				#tag.currSeq = 0
				#tag.prevSeq = 0


def main():
	app = QtGui.QApplication(sys.argv)
	global wispApp 
	wispApp = GUI_Setup()
	demo = RFID_Reader_App()
	wispApp.setWindowTitle("WISP Demo")
	sys.exit(app.exec_())

if __name__ == '__main__': main()
		