##################################### Variables and Constants #####################################
global tmp, tagType, hwVersion, snr, wispID, idEntry, data, newRow, plotData, rrsi, saturn, epc,\
	   entryCount, entry, accelX, accelY, accelZ, sensorData, temp, time, sensorData, host


host 		= "N/A"				#IP address for sllurp
<<<<<<< Updated upstream
<<<<<<< HEAD
tmp 		= "N/A"				#EPC
=======
tmp 		= "N/A"
camInfo		= "N/A"
>>>>>>> FETCH_HEAD
=======
tmp 		= "N/A"				#EPC
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream

#Accelerometer
accelX 		= 0 				#accelerometer wisp x tilt
accelY 		= 0 				#accelerometer wisp y tilt
accelZ 		= 0 				#accelerometer wisp z tilt

#Temperature
plotData 	= [] 				#plot temperature data

#Saturn
saturn 		= False

#Camera
<<<<<<< HEAD
imArray		= [128 for x in range(25200)]
boolPixelRecieved	= [0 for y in range(25200)]
=======
>>>>>>> FETCH_HEAD
x 			= 0
y 			= 50
currSeq = 0 					#current EPC sequence
prevSeq = 0 					#previous EPC sequence
sequence = 0 					#counter for the number of EPC sequences
count 	= 0
begin = 4
end = begin + 2
dataCount = 0
<<<<<<< HEAD
camTag = 0
=======
capturing = 0


acX = 0
acY = 0
acZ = 0

##################################### Localization #####################################

from cam import cam
from plot3D import *
import numpy as np

global myCam, USTags, numTx, tagCtr, activeFlg, win, readSum, log, \
runFlg, motion, logName, nowTags, pourCtr, p, fit


USTags 		= {}
numTx 		= 4
tagCtr 		= 0
activeFlg 	= 0
#myCam		= cam()
#numTx 		= 3 #actually it is 3 now


##### Data Log Structure #####
readSum 	= {'period':0, 'tagID': [], 'allTag': 0}
log 		= {}
runFlg 		= True
motion 		= {}
logName 	= 'test'
#logName 	= raw_input('Type in log File name:')
nowTags 	= {}
pourCtr 	= 0
=======
>>>>>>> Stashed changes

#Accelerometer
accelX 		= 0 				#accelerometer wisp x tilt
accelY 		= 0 				#accelerometer wisp y tilt
accelZ 		= 0 				#accelerometer wisp z tilt

#Temperature
plotData 	= [] 				#plot temperature data

#Saturn
saturn 		= False

<<<<<<< Updated upstream
#win = plot3D() 		# win is the 3D view Canvas name
>>>>>>> FETCH_HEAD
=======
#Camera
imArray		= [128 for x in range(25200)]
x 			= 0
y 			= 50
currSeq 	= 0 					#current EPC sequence
prevSeq 	= 0 					#previous EPC sequence
sequence 	= 0 					#counter for the number of EPC sequences
count 		= 0						#count for the number of WISP Cam enteries received 
fileCount 	= 0

#Multiple WISP Cams
camEntry = {}
camID = 0
>>>>>>> Stashed changes
