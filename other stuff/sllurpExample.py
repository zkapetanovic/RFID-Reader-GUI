from __future__ import print_function
import sllurp.llrp as llrp
from twisted.internet import reactor
import logging
import pkg_resources
import pprint

numTags = 0

logger = logging.getLogger('sllurp')
logger.setLevel(logging.INFO)

args = None

class readerConfig:
	def __init__(self, host = '192.168.10.5', port = llrp.LLRP_PORT, time = float(80),
				 debug = True, every_n = 1, antennas = '1', tx_power = 61, modulation = 'M8',
				 tari = 0, reconnect = True, logfile = 'logfile.log'):

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


def tagReportCallback(tagReport):
	global numTags
	tags = tagReport.msgdict['RO_ACCESS_REPORT']['TagReportData']

	if len(tags):
		logger.info('Saw Tag(s): {}'.format(pprint.pformat(tags)))

		for tag in tags:
			numTags += tag['TagSeenCount'][0]
			epc = tag['EPC-96']
			tagType = int(epc[0:8],2)
			print (tagType)
			#updateTagReport(epc)

	else:
		logger.info('No tags seen.')



def main():
	global args
	args = readerConfig()

	enabled_antennas = map(lambda x: int(x.strip()), args.antennas.split(','))

	fac = llrp.LLRPClientFactory(duration = args.time,
								 report_every_n_tags = args.every_n,
								 antennas = enabled_antennas,
								 tx_power = args.tx_power,
								 modulation = args.modulation,
								 tari = args.tari,
								 start_inventory = True,
								 disconnect_when_done = (args.time > 0),
								 reconnect = args.reconnect,
								 tag_content_selector = {
								 	'EnableROSpecID' : False,
								 	'EnableSpecIndex' : False,
								 	'EnableInventoryParameterSpecID' : False,
								 	'EnableAntennaID' : True,
								 	'EnableChannelIndex' : False,
								 	'EnablePeakRRSI' : True,
								 	'EnableFirstSeenTimestamp' : False,
								 	'EnableLastSeenTimestamp' : True,
								 	'EnableTagSeenCount' : True,
								 	'EnableAccessSpecID' : False 
								 })


	fac.addTagReportCallback(tagReportCallback)
	reactor.connectTCP(args.host, args.port, fac)
	reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, fac)
	reactor.run()

if __name__ == '__main__': main()