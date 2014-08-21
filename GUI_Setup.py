#!/usr/bin/env python


from PyQt4 import QtGui, Qt, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GUI_Setup(QtGui.QMainWindow):
	def __init__(self):
		super(GUI_Setup, self).__init__()
		self.initUI()
		self.resize(1190, 530)

	def initUI(self):

		#### Main Table ####
		self.main_frame = QWidget()
		self.mainTable = QtGui.QTableWidget(0, 7, self)
		self.mainTable.setFont(QFont('Courier New', 8))
		self.mainTable.setHorizontalHeaderLabels(('TIME', 'WISP ID', 'TAG TYPE', 'EPC', 'SENSOR DATA', 'SNR', 'RSSI'))
		self.mainTable.horizontalHeader().setStretchLastSection(True)
		self.mainTable.setGeometry(10, 120, 700, 330)

		#### Buttons ####
		self.startButton = QtGui.QPushButton('Start', self)
		self.startButton.setGeometry(30, 460, 100, 30)

		self.stopButton = QtGui.QPushButton('Stop', self)
		self.stopButton.setGeometry(140, 460, 100, 30)

		self.saturnButton = QtGui.QPushButton('Saturn', self)
		self.saturnButton.setGeometry(250, 460, 100, 30)

		self.local3DButton = QtGui.QPushButton('Localization', self)
		self.local3DButton.setGeometry(360, 460, 140, 30)

		#### Localization ####
		self.numPoints = QtGui.QComboBox(self)
		self.numPoints.setEditable(False)
		self.numPoints.addItem('2')
		self.numPoints.addItem('3')
		self.numPoints.addItem('4')

		self.ch1Label = QtGui.QLabel("Channel 1:", self)
		self.ch1Label.setFont(QFont('Arial', 10))

		self.ch2Label = QtGui.QLabel("Channel 2:", self)
		self.ch2Label.setFont(QFont('Arial', 10))

		self.ch3Label = QtGui.QLabel("Channel 3:", self)
		self.ch3Label.setFont(QFont('Arial', 10))

		self.ch4Label = QtGui.QLabel("Channel 4:", self)
		self.ch4Label.setFont(QFont('Arial', 10))

		self.ch1 = QtGui.QTextEdit(self)
		self.ch1.setFixedHeight(25)
		self.ch1.setFixedWidth(60)
		self.ch1.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		self.ch2 = QtGui.QTextEdit(self)
		self.ch2.setFixedHeight(25)
		self.ch2.setFixedWidth(60)
		self.ch2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		self.ch3 = QtGui.QTextEdit(self)
		self.ch3.setFixedHeight(25)
		self.ch3.setFixedWidth(60)
		self.ch3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		self.ch4 = QtGui.QTextEdit(self)
		self.ch4.setFixedHeight(25)
		self.ch4.setFixedWidth(60)
		self.ch4.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		self.pointsLabel = QtGui.QLabel("Select Number of Points:", self)
		self.pointsLabel.setFont(QFont('Arial', 10))

		self.chanLabel = QtGui.QLabel("Channel Coordinates (x, y, z):", self)
		self.chanLabel.setFont(QFont('Arial', 10))

		self.localTable = QtGui.QTableWidget(0, 2, self)
		self.localTable.setFont(QFont('Courier New', 10))
		self.localTable.horizontalHeader().setStretchLastSection(True)
		self.localTable.setHorizontalHeaderLabels(('WISP ID', 'Localization (x, y, z)'))
		self.localTable.setFixedWidth(432)


		#### Accelerometer ####
		self.xAccel = QtGui.QLabel(self)
		self.yAccel = QtGui.QLabel(self)
		self.zAccel = QtGui.QLabel(self)
		
		self.sliderY = QtGui.QSlider(QtCore.Qt.Vertical, self)
		self.sliderX = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.sliderZ = QtGui.QSlider(QtCore.Qt.Vertical, self)


		########## Image Capture ##########
		self.xVal = QtGui.QTextEdit(self)
		self.xVal.setFixedWidth(100)
		self.xVal.setFixedHeight(25)
		self.xVal.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		
		self.yVal = QtGui.QTextEdit(self)
		self.yVal.setFixedWidth(100)
		self.yVal.setFixedHeight(25)
		self.yVal.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		
		self.xLabel = QtGui.QLabel("    X-Value (0 - 255):       ")
		self.yLabel = QtGui.QLabel("    Y-Value (0 - 255):       ")

		self.captureButton = QtGui.QPushButton("Enter Values")
		self.captureButton.setFixedHeight(30)
		self.captureButton.setFixedWidth(100)

		self.image = Figure()
		self.imageCanvas = FigureCanvas(self.image)


		########## Readers ##########
		self.readerFrame = QtGui.QFrame(self)
		self.readerFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
		self.readerFrame.setLineWidth(4)
		self.readerFrame.setGeometry(10, 22, 700, 90)
		
		self.readerLabel = QtGui.QLabel("Reader Select:", self)
		self.readerLabel.setGeometry(10, 3, 110, 20)
		self.readerLabel.setFont(QFont('Arial', 12))
		
		self.usrpSelect = QtGui.QRadioButton("USRP", self)
		self.usrpSelect.setGeometry(15, 28, 100, 20)
		self.usrpSelect.setObjectName("usrp")
		self.usrpSelect.setFont(QFont('Arial', 10))
		
		self.impinjSelect = QtGui.QRadioButton("Impinj", self)
		self.impinjSelect.setGeometry(15, 55, 100, 20)
		self.impinjSelect.setObjectName("impinj")
		self.impinjSelect.setFont(QFont('Arial', 10))
		
		self.ipLabel = QtGui.QLabel("IP Address:", self)
		self.ipLabel.setGeometry(55, 87, 100, 10)
		self.ipLabel.setFont(QFont('Arial', 10))
		
		self.ipAddress = QtGui.QTextEdit(self)
		self.ipAddress.setGeometry(140, 80, 200, 25)
		self.ipAddress.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		
		self.connectButton = QtGui.QPushButton("Connect", self)
		self.connectButton.setGeometry(600, 75, 100, 30)
		self.connectButton.setObjectName("readerSelect")

		######### Graph ##########		
		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)

		######### Tabs ##########

		#Image Capture
		self.imageLayout = QtGui.QGridLayout()
		self.imageLayout.setHorizontalSpacing(30)
		self.imageLayout.addWidget(self.xLabel, 1, 0)
		self.imageLayout.addWidget(self.xVal, 1, 4)
		self.imageLayout.addWidget(self.yLabel, 2, 0)
		self.imageLayout.addWidget(self.yVal, 2, 4)
		self.imageLayout.addWidget(self.captureButton, 3, 4)
		self.imageLayout.addWidget(self.imageCanvas, 5, 0, 5, 5)

		#Localization
		localLayout = QtGui.QGridLayout()
		localLayout.setRowMinimumHeight(0, 20)
		localLayout.addWidget(self.pointsLabel, 0, 0)
		localLayout.addWidget(self.numPoints, 0, 1)
		localLayout.addWidget(self.chanLabel, 1, 0)
		localLayout.addWidget(self.ch1Label, 2, 0)
		localLayout.addWidget(self.ch2Label, 3, 0)
		localLayout.addWidget(self.ch3Label, 4, 0)
		localLayout.addWidget(self.ch4Label, 5, 0)
		localLayout.addWidget(self.ch1, 2, 1)
		localLayout.addWidget(self.ch2, 3, 1)
		localLayout.addWidget(self.ch3, 4, 1)
		localLayout.addWidget(self.ch4, 5, 1)
		localLayout.addWidget(self.localTable, 6, 0)
		
		#Temperature
		self.tempLayout = QtGui.QGridLayout()
		self.tempLayout.addWidget(self.canvas, 0, 0)
		
		#Accelerometer
		accelLayout = QtGui.QGridLayout()
		accelLayout.setRowMinimumHeight(0, 20)
		accelLayout.addWidget(self.yAccel, 0, 0)
		accelLayout.addWidget(self.sliderY, 1, 0)
		accelLayout.addWidget(self.zAccel, 0, 5)
		accelLayout.addWidget(self.sliderZ, 1, 5)
		accelLayout.addWidget(self.xAccel, 5, 3, QtCore.Qt.AlignCenter)
		accelLayout.addWidget(self.sliderX, 6, 3)
		
		tabFrame = QtGui.QFrame(self)
		tabFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
		tabFrame.setLineWidth(4)
		tabFrame.setGeometry(720, 30, 460, 465)		
		
		tabs = QtGui.QTabWidget(self)
		tabs.resize(450, 480)
		tabs.move(720, 10)
			
		accelTab = QtGui.QWidget()
		tempTab = QtGui.QWidget()
		localTab = QtGui.QWidget()
		imageTab = QtGui.QWidget()

		tabs.addTab(localTab, "Localization")
		tabs.addTab(accelTab, "Accelerometer")
		tabs.addTab(tempTab, "Temperature")
		tabs.addTab(imageTab, "Image Capture")

		accelTab.setLayout(accelLayout)
		tempTab.setLayout(self.tempLayout)
		localTab.setLayout(localLayout)
		imageTab.setLayout(self.imageLayout)
		
		########## Stylesheet ##########
		Stylesheet = """
		QPushButton {border: 1px solid black; border-radius: 6px;}
		QPushButton#Stop {border: 1px solid #F21B34; border-radius: 6px;}
		QPushButton#Start {border: 1px solid #5BD463; border-radius: 6px;}
		QTabWidget:pane{border: 1px sp;od #C2C7CB;}
		QTabWidget:tab-bar{left: 0px; border: none;}
		QTabBar: tab {background: qlineargradient(x1: 0, y1: 0, x2:0, y2: 1,\
		stop: 0 #E1E1E1, stop: 0.4 #DDDDDD, stop 0.5 #D8D8D8, stop: 1.0 #D3D3D3);\
		border: 1px solid #C4C4C3; border-top-left-radius: 2px;\
		border-top-right-radius: 4px; min-width: 8px; padding: 2px;}
		QTabBar:tab:selected {border-color: #9B9B9B; border-bottom-color: #C2C7CB;}
		QTabBar:tab:!selected {margin-top: 2px;}
		QTableWidget {background-color: qlineargradient(x1; 0, y1: 0, x2: 0.5, y2: 0.5,\
		stop: 0 #FF92BB, stop: 1 white);}
		"""
		
		self.setStyleSheet(Stylesheet)	

		self.show()

