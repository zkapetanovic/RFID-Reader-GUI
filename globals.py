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
imArray		= ['invalid' for x in range(25200)]
x 			= 0
y 			= 60
currSeq 	= 0 					#current EPC sequence
prevSeq 	= 0 					#previous EPC sequence
sequence 	= 0 					#counter for the number of EPC sequences
count 		= 0						#count for the number of WISP Cam enteries received 
fileCount 	= 0

#Multiple WISP Cams
camEntry = {}
camID = 0
