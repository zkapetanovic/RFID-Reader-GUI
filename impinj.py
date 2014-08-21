#!/usr/bin/env python

"""
 Created on Thursday July, 17, 2014
 @author Zerina Kapetanovic
"""
#169.254.128.56
from __future__ import print_function
import logging
import pkg_resources
import pprint
import sys
import threading

import sllurp.llrp as llrp
from sllurp.llrp_proto import LLRPROSpec, ModeIndex_Name2Type

from twisted.internet import reactor, defer


from updateTagReport import UpdateTagReport
import globals as tag

tagsSeen = 0
logger = logging.getLogger('sllurp')
args = None

class readerConfig:
	def __init__(self, host = '192.168.10.5', port = llrp.LLRP_PORT, duration = float(80),
				 every_n = 1, antennas = '1', standalone = True,
				 tx_power = 31, modulation = 'WISP5', reconnect = True,
				 tari = 0, logfile = 'logfile.log', debug = True):

		self.host 		= host
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



class ImpinjReader(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		impinj = reactor
		self.impinj = impinj


	def run(self):
		global args
		args = readerConfig()
		print (args.host)
		self.initReader()

	def politeShutdown(self, factory):
		return factory.politeShutdown()                                   


	def tagReportCallback(self, tagReport):
		global tagsSeen
		tags = tagReport.msgdict['RO_ACCESS_REPORT']['TagReportData']

		if len(tags):
			#logger.info('saw tag(s): {}'.format(pprint.pformat(tags)))
			for tag in tags:
				tagsSeen 	+= tag['TagSeenCount'][0]
				epc 		 = tag['EPC-96']
				rssi 		 = tag['PeakRSSI'][0]
				time 		 = tag['LastSeenTimestampUTC'][0]
				snr 		 = "N/A"

				tagReport = UpdateTagReport()
				tagReport.parseData(epc, rssi, snr, time)


	def initReader(self):
		global args
		args = readerConfig()


		logger.setLevel(logging.INFO)
		logFormat = '%(asctime)s %(name)s: %(levelname)s: %(message)s'
		formatter = logging.Formatter(logFormat)
		fHandler = logging.FileHandler(args.logfile)
		fHandler.setFormatter(formatter)
		logger.addHandler(fHandler)

		enabled_antennas = map(lambda x: int(x.strip()), args.antennas.split(','))

		reader = llrp.LLRPReaderThread('192.168.10.5',
								  llrp.LLRP_PORT,
								  duration = ((args.duration) < 0),
								  report_every_n_tags = args.every_n, 
								  antennas = args.antennas, 
								  start_inventory = True, 
								  disconnect_when_done = True, 
								  standalone = args.standalone, 
								  tx_power = args.tx_power, 
								  modulation = args.modulation,
								  reconnect = args.reconnect)
		reader.setDaemon(True)
		reader.addCallback('RO_ACCESS_REPORT', self.tagReportCallback)
		reader.start()

		print ("Start")

		try:
			while reader.isAlive():
				reader.join(0.1)
		except KeyboardInterrupt:
			logger.fatal('interrupted; stopping inventory')
			reactor.callFromThread(reactor.callLater, 1, reactor.stop)
			reader.join(1.5)

		#logger.info('total # of tags seen by callback: {}'.format(tagsSeen))