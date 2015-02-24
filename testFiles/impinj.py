from __future__ import print_function
import logging
import pkg_resources
import pprint
import threading

import sllurp.llrp as llrp
from sllurp.llrp_proto import LLRPROSpec, ModeIndex_Name2Type
from twisted.internet import reactor, defer

tagsSeen = 0

logger = logging.getLogger('sllurp')
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logfile.log'))

args = None
global check
class readerConfig:
	def __init__(self, host = '169.254.115.176', port = llrp.LLRP_PORT, time = float(80),
				 debug = True, every_n = 1, antennas = '1', tx_power = 61, modulation = 'WISP5',
				 tari = 7140, reconnect = True, logfile = 'logfile.log'):

		self.host 		= host
		self.port 		= port
		self.time 		= time
		self.debug 		= debug
		self.every_n	= every_n
		self.antennas 	= antennas
		self.tx_power	= tx_power
		self.modulation = modulation
		self.tari		= tari
		self.reconnect  = reconnect
		self.logfile	= logfile


def politeShutdown(factory):
	return factory.politeShutdown()


def tagReportCallback(llrpMsg):
	"""Function to run each time the reader reports seeing tags."""
		
	global tagsSeen
	tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
	tags.reverse()

	if len(tags):
		for tag in tags:
			tagsSeen 	 += tag['TagSeenCount'][0]
			epc 		 = tag['EPC-96']
			rssi 		 = tag['PeakRSSI'][0]
			time 		 = tag['LastSeenTimestampUTC'][0]
			readData	  = tag['OpSpecResult']
			snr 		 = "N/A"
			check = int(epc[2:4], 16)
			print (readData)
			logger.info('Saw Tag(s): {}'.format(pprint.pformat(tags)))

def access (proto):
    readSpecParam = None
    print ("Entered Access")
    readSpecParam = {
        'OpSpecID': 0,
        'MB': 1,
        'WordPtr': 0,
        'AccessPassword': 0,
        'WordCount': 0				
        }
    proto.startAccess(readWords = readSpecParam)

    #return proto.startAccess(readWords=readSpecParam)

def main():
	global args
	args = readerConfig()

	enabled_antennas = map(lambda x: int(x.strip()), args.antennas.split(','))
	global factory
	factory = llrp.LLRPClientFactory(duration = args.time,
							report_every_n_tags = args.every_n,
							antennas = enabled_antennas,
							tx_power = args.tx_power,
							modulation = args.modulation,
							tari = args.tari,
							start_inventory = True,
							disconnect_when_done = (args.time > 0),
							reconnect = args.reconnect,
							tag_content_selector = {
								'EnableROSpecID' : True,
								'EnableSpecIndex' : True,
								'EnableInventoryParameterSpecID' : True,
								'EnableAntennaID' : True,
								'EnableChannelIndex' : False,
								'EnablePeakRRSI' : True,
								'EnableFirstSeenTimestamp' : False,
								'EnableLastSeenTimestamp' : True,
								'EnableTagSeenCount' : True,
								'EnableAccessSpecID' : True 
								})


	factory.addTagReportCallback(tagReportCallback)
	factory.addStateCallback(llrp.LLRPClient.STATE_INVENTORYING, access)
	reactor.connectTCP(args.host, args.port, factory)
	reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, factory)
	reactor.run()

if __name__ == '__main__': main()
