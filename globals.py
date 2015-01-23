
##################################### Variables and Constants #####################################
global tmp, tagType, hwVersion, snr, wispID, idEntry, data, newRow, plotData, rrsi, saturn, epc,\
	   entryCount, entry, accelX, accelY, accelZ, sensorData, temp, time, sensorData, host

host 		= "N/A"				#IP address for sllurp
tmp 		= "N/A"				#EPC
tagType 	= "N/A"
hwVersion 	= "N/A"
snr 		= "N/A"
rssi		= "N/A"
sensorData 	= "N/A"
epc 		= "N/A"
time		= 0
wispID 		= 0

newRow 		= 0 				#row counter for main table
entryCount  = 0 				#counts the number of entries seen
idEntry 	= {} 				#stores all tags seen
data 		= [] 				#data to be displayed in main table
entry 		= ()

#Accelerometer
accelX 		= 0 				#accelerometer wisp x tilt
accelY 		= 0 				#accelerometer wisp y tilt
accelZ 		= 0 				#accelerometer wisp z tilt

#Temperature
plotData 	= [] 				#plot temperature data

#Saturn
saturn 		= False

#Camera
imArray			= [-1 for x in range(25200)]
x 				= 0
y 				= 50
currSeq 		= 0 					#current EPC sequence
prevSeq 		= 0 					#previous EPC sequence
sequence 		= 0 					#counter for the number of EPC sequences
index 			= 0
dataCount 		= 0
camTag 			= 0
packetCount		= 0
epcPacket 		= 0
getPacket		= []
dataIndex 		= []
retrieve 		= 0

#Threads
impinjThread = 0


###################### LOCALIZATION ######################
from cam import cam
from plot3D import*
import numpy as np

global myCam,USTags,numTx,tagCtr,activeFlg,win,readSum,log, \
		runFlg,motion,logName,nowTags,pourCtr,p,fit
#myCam = cam()
USTags = {}
#numTx = 3 # actually it is 3 now
numTx=4
tagCtr=0
activeFlg=0


##################Data Log Structure##################################
readSum={'period':0,'tagsID':[],'allTag':0}
log={}
runFlg = True
motion={}
logName = 'test'
#logName = raw_input('Type in log File name:')
nowTags={}
pourCtr=0

################# System Location parameter###########################
#3D location of ultrasound beams
#p = np.array([[-16.5,14.25,0],[-16.5,-14.5,0],[16.5,14.25,0],[16.5,-14.5,0]],dtype = np.float32)
#3D location of Tetrahedron
a= 60.33#the side length
c= 30.48 #the center length 
h= 0.866*a#the middle line of the triangle
offset = 0.5 # the sensor length
p = np.array([[0,0.816*a,-0.289*a-offset],[-1*a/2,0,offset], [a/2,0,offset], [0,c/2,0.866*c-h+offset]],dtype=np.float32)

#p = np.array([[-33.29,-18.793,0],[33.29,-18.793,0],[0,38.5946,0],[0,0,-20.5]],dtype = np.float32)

#line fit result(may not need in the future)
#line fit for wetlab
#fit = np.array([[1.014,-4.512],[1.027,-101.3],[1.038,-202.5],[1.07,-323.3]])
#line fit parameter 2014_2_21
#fit = np.array([[1.063,-11.59],[1.063,-114.2],[1.071,-219.5],[1.07,-323.3]])
#line fit 2014_2_22
#measurement accuracy +/- 0.8cm 
#fit = np.array([[1.058,-10.23],[1.06,-112.8],[1.069,-218.1],[1.067,-321.3]])
#fit = np.array([[1.058,-10.23],[1.60,-112.8],[1.069,-218.1],[1.067,-321.3]])
#line fit parameter for 65.5 inch high
#fit = np.array([[0.9142,15.28],[0.9531,-83.55],[0.8002,-118.6],[0.9011,-243.8]])
#fit = np.array([[0.8553,10.28],[1.005,-102.6],[0.8781,-161.8],[0.9718,-284.6]])
 
#fit = np.array([[1.045,-6.583],[1.067,-110.5],[1.061,-211.2],[1.971,-670.0]])
#fit = np.array([[1.062,-6.942],[1.27,-151.9],[0.6654,-105.4],[0.6068,-147.9]])
#fit = np.array([[1.062,-6.942],[1.067,-110.5],[1.061,-217.2],[1.971,-670.0]])

#fit using refined tested result
#average fitting
#fit = np.array([1.02*[1,-8.419],[1,-8.419-88.98],[1,-8.419-88.98-89.1573],[1,-8.419-88.98-89.1573-88.25]])
#fit =1.02*fit

fit = np.array([[1,-10.33],[1,-8.419-93.89],[1,-8.419-93.89*2],[1,-8.419-93.89*3]])
fit =1.02*fit
# 0 degree AOA fitting
#fit = np.array([[1.018,-6.763],[1.06,-112.8],[1.069,-218.1],[1.067,-321.3]])



