from __future__ import print_function
import argparse
import logging
import pprint
import time
from twisted.internet import reactor, defer

import sllurp.llrp as llrp

tagReport = 0

logger = logging.getLogger('sllurp')
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logfile.log'))
args = None


def access (proto):
    proto.startAccess(readWords = 1)
    print ("Entered Access")

def politeShutdown (factory):
    return factory.politeShutdown()

def tagReportCallback (llrpMsg):
    """Function to run each time the reader reports seeing tags."""
    global tagReport
    tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
    if len(tags):
        logger.info('saw tag(s): {}'.format(pprint.pformat(tags)))
    else:
        logger.info('no tags seen')
        return
    for tag in tags:
        tagReport += tag['TagSeenCount'][0]



def main ():
	
	fac = llrp.LLRPClientFactory(disconnect_when_done=True,
            antennas = 1,
            modulation= 'FMO',
            tari= 6520,
            start_inventory=True,
            tx_power= 61,
            report_every_n_tags= 1,
            tag_content_selector={
                'EnableROSpecID': False,
                'EnableSpecIndex': False,
                'EnableInventoryParameterSpecID': False,
                'EnableAntennaID': True,
                'EnableChannelIndex': False,
                'EnablePeakRRSI': True,
                'EnableFirstSeenTimestamp': False,
                'EnableLastSeenTimestamp': True,
                'EnableTagSeenCount': True,
                'EnableAccessSpecID': True
            })

    # tagReportCallback will be called every time the reader sends a TagReport
    # message (i.e., when it has "seen" tags).
	fac.addTagReportCallback(tagReportCallback)

    # start tag access once inventorying
	fac.addStateCallback(llrp.LLRPClient.STATE_INVENTORYING, access)

	reactor.connectTCP('169.254.115.176', llrp.LLRP_PORT, fac, timeout=3)

    # catch ctrl-C and stop inventory before disconnecting
	reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, fac)

	reactor.run()

if __name__ == '__main__': main()