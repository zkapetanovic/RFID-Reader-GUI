from __future__ import print_function
import logging
import pkg_resources
import pprint
from ast import literal_eval
import threading
import sllurp.llrp as llrp
from sllurp.llrp_proto import LLRPROSpec, ModeIndex_Name2Type
from twisted.internet import reactor, defer

from updateTagReport import UpdateTagReport
import globals 

tagsSeen = 0

logger = logging.getLogger('sllurp')
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logfile.log'))

args = None

class readerConfig:
	def __init__(self, host = globals.host, port = llrp.LLRP_PORT, time = float(80),
				 debug = True, every_n = 1, antennas = '1', tx_power = 61, modulation = 'WISP5pre',
				 tari = 12500, reconnect = True, logfile = 'logfile.log'):

		self.host 		= globals.host
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

class Reader(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		impinj = reactor
		self.impinj = impinj
		self.tagReport = UpdateTagReport()
		self.readData = 0

	def run(self):
		self.initReader() 

	def politeShutdown(self, factory):
		return factory.politeShutdown()


	def tagReportCallback(self, llrpMsg):
		"""Function to run each time the reader reports seeing tags."""
			
		global tagsSeen
		tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
		tags.reverse()
			
		if len(tags):
			for tag in tags:
				tagsSeen 	 += tag['TagSeenCount'][0]
				epc 		  = tag['EPC-96']
				rssi 		  = tag['PeakRSSI'][0]
				time 		  = tag['LastSeenTimestampUTC'][0]
				snr 		  = "N/A"

				try:
					opSpec	  = tag['OpSpecResult']['ReadData']
					data = opSpec.encode("string_escape")
					self.readData = data.replace('\\x', '')

				except:
					logger.error('Read CMD not excuted, cannot retrieve data')
					#readData = 0
				
				'''
				except KeyError as ke:
					print(ke)
					import ipdb; ipdb.set_trace()
				'''
				logger.info('Saw Tag(s): {}'.format(pprint.pformat(tags)))				
				self.tagReport.parseData(epc, rssi, snr, time, self.readData)

		else:
			#globals.tmp = "N/A"
			#logger.info('no tag seen')
			return

	def access (self, proto):
	    readSpecParam = None
	    readSpecParam = {
	        'OpSpecID': 0,
	        'MB': 0, 
	        'WordPtr': globals.wordPtr,
	        'AccessPassword': 0,
	        'WordCount': 15
	        }
	    
	    proto.startAccess(readWords = readSpecParam) #removed return
	    #tag.retreive = 0
	    #return proto.startAccess(readWords=readSpecParam)


	def initReader(self):
		global args
		args = readerConfig()

		enabled_antennas = map(lambda x: int(x.strip()), args.antennas.split(','))

		self.factory = llrp.LLRPClientFactory(duration = args.time,
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

		self.factory.addStateCallback(llrp.LLRPClient.STATE_INVENTORYING, self.access)
		self.factory.addTagReportCallback(self.tagReportCallback)
		
		reactor.connectTCP(args.host, args.port, self.factory)
		reactor.addSystemEventTrigger('before', 'shutdown', self.politeShutdown, self.factory)
		reactor.run()