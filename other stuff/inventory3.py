#!/usr/bin/env python

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
#169.254.128.56


class readerConfig:
	def __init__(self, host = globals.host, port = llrp.LLRP_PORT, duration = float(80),
				 every_n = 1, antennas = '1', standalone = True,
<<<<<<< Updated upstream
<<<<<<< HEAD
				 tx_power = 61, modulation = 'WISP5', reconnect = True,
=======
				 tx_power = 31, modulation = 'WISP5', reconnect = True,
>>>>>>> FETCH_HEAD
=======
				 tx_power = 61, modulation = 'WISP5', reconnect = True,
>>>>>>> Stashed changes
				 tari = '0', logfile = 'logfile.log', debug = True):

		self.host 		= globals.host
		self.port 		= port
		self.duration 	= duration
		self.debug 		= debug
		self.every_n	= every_n
		self.antennas 	= antennas
		self.tx_power	= tx_power
		self.modulation = modulation
		self.tari		= tari
		self.reconnect  = reconnect
		self.logfile	= logfile
		self.standalone = standalone



class Reader(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		impinj = reactor
		self.impinj = impinj

	def run(self):
		self.initReader()

	def tagSeenCallback (self, llrpMsg):
	    """Function to run each time the reader reports seeing tags."""
	    global tagsSeen
	    tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
	    tags.reverse()
	    if len(tags):
			logger.info('saw tag(s): {}'.format(pprint.pformat(tags)))

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
		args = readerConfig()
		logger.setLevel(logging.INFO)
		logFormat = '%(asctime)s %(name)s: %(levelname)s: %(message)s'
		formatter = logging.Formatter(logFormat)
		fHandler = logging.FileHandler(args.logfile)
		fHandler.setFormatter(formatter)
		logger.addHandler(fHandler)
		enabled_antennas = map(lambda x: int(x.strip()), args.antennas.split(','))
		self.reader = llrp.LLRPReaderThread(args.host,
								  llrp.LLRP_PORT,
								  duration = args.duration,
								  report_every_n_tags = args.every_n, 
								  antennas = args.antennas, 
								  start_inventory = True, 
								  disconnect_when_done = True, 
								  standalone = args.standalone, 
								  tx_power = args.tx_power, 
								  modulation = args.modulation,
								  reconnect = args.reconnect,
								  tari = 25)

		self.reader.setDaemon(True)
		self.reader.addCallback('RO_ACCESS_REPORT', self.tagSeenCallback)
		self.reader.start()
		print ("Start")

		try:
			while self.reader.isAlive():
				self.reader.join(0.1)
		except KeyboardInterrupt:
			logger.fatal('interrupted; stopping inventory')
			self.impinj.callFromThread(reactor.callLater, 1, self.impinj.stop)
			self.reader.join(1.5)

		logger.info('total # of tags seen by callback: {}'.format(tagsSeen))

