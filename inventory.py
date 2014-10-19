from __future__ import print_function
import logging
import pkg_resources
import pprint
import threading

import sllurp.llrp as llrp
from sllurp.llrp_proto import LLRPROSpec, ModeIndex_Name2Type

from twisted.internet import reactor

from updateTagReport import UpdateTagReport
import globals

tagsSeen = 0

logger = logging.getLogger('sllurp')
logger.setLevel(logging.INFO)
#169.254.128.56
args = None

class readerConfig:
	def __init__(self, host = globals.host, port = llrp.LLRP_PORT, time = float(80),
				 debug = True, every_n = 1, antennas = '1', tx_power = 61, modulation = 'WISP5',
				 tari = 25, reconnect = True, logfile = 'logfile.log'):

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
		self.impinj  = impinj


	def run(self):
		self.initReader()
		
		
	def politeShutdown(factory):
		return factory.politeShutdown()


	def tagReportCallback(self, llrpMsg):
		"""Function to run each time the reader reports seeing tags."""
		
		global tagsSeen
		tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
		tags.reverse()
		
		if len(tags):
			logger.info('Saw Tag(s): {}'.format(pprint.pformat(tags)))

			for tag in tags:
				tagsSeen += tag['TagSeenCount'][0]
				epc 		 = tag['EPC-96']
				rssi 		 = tag['PeakRSSI'][0]
				time 		 = tag['LastSeenTimestampUTC'][0]
				snr 		 = "N/A"

				tagReport = UpdateTagReport()
				tagReport.parseData(epc, rssi, snr, time)

			else:
				globals.tmp = "N/A"
				logger.info('no tags seen')
				return



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


		self.factory.addTagReportCallback(self.tagReportCallback)
		reactor.connectTCP(args.host, args.port, self.factory)
		reactor.addSystemEventTrigger('before', 'shutdown', self.politeShutdown, self.factory)
		reactor.run()

