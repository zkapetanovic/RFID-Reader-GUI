#!/usr/bin/env python
"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovic
"""
### GUI ###
from PyQt4 import QtGui, Qt, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import numpy as np

### GRAPHING ###
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys, threading, time
import pkg_resources			#SLLURP needs this....idk why

### MODULES ###
from GUI_Setup import GUI_Setup
from inventory import Reader
from updateTagReport import UpdateTagReport
from saturn import SaturnDemo
from localThread import localThread
import globals as tag


class RFID_Reader_App:
	def __init__(self):
		
		tag.impinjThread = Reader()
		self.saturnThread = SaturnDemo()
		self.usrpStart = False
		self.impinjStart = False

		self.runStarted = 0
		self.pause = 0

		wispApp.startButton.clicked.connect(self.start)
		wispApp.local3DButton.clicked.connect(self.initLocalization)
		wispApp.connectButton.clicked.connect(self.readerSelect)
		wispApp.saturnButton.clicked.connect(self.initSaturn)
		wispApp.captureButton.clicked.connect(self.captureImage)
		wispApp.pauseButton.clicked.connect(self.pauseRun)
		wispApp.clearButton.clicked.connect(self.clearTable)


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
			self.timer.start(100)
			self.initReader()

		if self.pause == 1:
			tag.impinjThread.factory.resumeInventory()
			self.pause = 0


	def stop(self):
		tag.impinjThread.impinj.stop()
		self.timer.stop()


	def pauseRun(self):
		tag.impinjThread.factory.pauseInventory()
		self.pause = 1

	def clearTable(self):
		tag.data = []
		tag.idEntry = []
		tag.newRow = 0
		tag.entryCount = 0
		wispApp.mainTable.clearContents()		


	def initReader(self):
		if self.impinjStart == True:
			tag.impinjThread.daemon = True
			wispApp.statusLabel.setText("<b>Status</b>: Charging")
			tag.impinjThread.start()
		elif self.usrpStart == True:
			global usrp_tb
			self.usrp_tb = my_top_block()
			self.usrp_tb.start()


	def initSaturn(self):
		self.saturnThread.daemon = True
		self.saturnThread.start()
		tag.saturn = True

	def initLocalization(self):
		self.thread = localThread()
		self.thread.daemon = True
		self.thread.start()


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
			wispApp.xAccel.setText(" X '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelX)
			wispApp.yAccel.setText(" Y '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelY)
			wispApp.zAccel.setText(" Z '%' Tilt: " + "\n" + '%6.2f%%' % tag.accelZ)

			wispApp.sliderY.setValue(tag.accelY)
			wispApp.sliderX.setValue(tag.accelX)
			wispApp.sliderZ.setValue(tag.accelZ)

			if tag.saturn == True:
				self.saturnThread.setAngles(tag.accelX, tag.accelY, tag.accelZ)


	def captureImage(self):
		tag.x = str("%s" % wispApp.xVal.toPlainText())
		tag.y = str("%s" % wispApp.yVal.toPlainText())
		if tag.tagType == "CA":
			wispApp.statusLabel.setText("<b>Status</b>: Transmitting data")
			rows 	= 144
			columns = 175

			tag.x = str("%s" % wispApp.xVal.toPlainText())
			tag.y = str("%s" % wispApp.xVal.toPlainText())
			
			if tag.index >= 25199 or int(tag.epc[2:4], 16) == 255:		
				wispApp.statusLabel.setText("Status: Image captured")
				for i in tag.imArray:
					if i <= tag.x: 	i = 0
					elif i > tag.y: i = 255

				plt.cla()
				plt.clf()
				mat_image = np.reshape(tag.imArray, (rows, columns)) / 255.0
				plt.gray()			
				image = wispApp.image.add_subplot(111)
				image.clear()
				ax = wispApp.image.gca()
				ax.set_axis_off()
				image.imshow(mat_image)
				wispApp.imageCanvas.draw()



def main():
	app = QtGui.QApplication(sys.argv)
	global wispApp 
	wispApp = GUI_Setup()
	demo = RFID_Reader_App()
	wispApp.setWindowTitle("WISP Demo")
	sys.exit(app.exec_())

if __name__ == '__main__': main()
		