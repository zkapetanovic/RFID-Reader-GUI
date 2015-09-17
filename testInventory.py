from __future__ import print_function
import argparse
import logging
import pprint
import time
from twisted.internet import reactor, defer

import sllurp.llrp as llrp
from sllurp.llrp_proto import Modulation_Name2Type, DEFAULT_MODULATION, \
     Modulation_DefaultTari


from updateTagReport import UpdateTagReport

numTags = 0
logger = logging.getLogger('sllurp')

args = None

def finish (_):
    logger.info('total # of tags seen: {}'.format(numTags))
    if reactor.running:
        reactor.stop()

def politeShutdown (factory):
    return factory.politeShutdown()

def tagReportCallback (llrpMsg):
    """Function to run each time the reader reports seeing tags."""
    global numTags
    tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
    if len(tags):
        pass
        #logger.info('saw tag(s): {}'.format(pprint.pformat(tags)))
    else:
        logger.info('no tags seen')
        return
    for tag in tags:
        numTags += tag['TagSeenCount'][0]

def readerConfig():
    settings = {'modulation' : 'FM0',
                'tari'       : 25000,
                'port'       : llrp.LLRP_PORT, 
                'time'       : 0,
                'debug'      : True, 
                'every_n'    : 1,
                'reconnect'  : True,
                'logfile'    : 'logfile.log',
                'tx_power'   : 61, 
                'antennas'   : '1', 
                'host'       : '169.254.128.56'
                }
    return settings
        
def init_logging ():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler('logfile.log'))
    logger.log(logLevel, 'log level: {}'.format(logging.getLevelName(logLevel)))

def main ():
    #parse_args()
    init_logging()
    args = readerConfig();
    # special case default Tari values
    #if args['modulation'] in Modulation_DefaultTari:
    #    t_suggested = Modulation_DefaultTari[args['modulation']]
    #    if args['tari']:
    #        logger.warn('recommended Tari for {} is {}'.format(args['modulation'],
    #                    t_suggested))
    #    else:
    ##        args['tari'] = t_suggested
     #       logger.info('selected recommended Tari of {} for {}'.format(args['tari'],
     #                   args['modulation']))

    enabled_antennas = map(lambda x: int(x.strip()), args['antennas'].split(','))

    # d.callback will be called when all connections have terminated normally.
    # use d.addCallback(<callable>) to define end-of-program behavior.
    d = defer.Deferred()
    d.addCallback(finish)

    fac = llrp.LLRPClientFactory(onFinish=d,
            duration= 0,
            report_every_n_tags=1,
            antennas=enabled_antennas,
            tx_power= 0,
            modulation='FM0',
            tari= '7140',
            session= 2,
            tag_population= 4,
            start_inventory=True,
            disconnect_when_done= False,
            reconnect= True,
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
                'EnableAccessSpecID': False
            })

    # tagReportCallback will be called every time the reader sends a TagReport
    # message (i.e., when it has "seen" tags).
    fac.addTagReportCallback(tagReportCallback)
    reactor.connectTCP(args['host'], args['port'], fac, timeout=3)
    
    # catch ctrl-C and stop inventory before disconnecting
    reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, fac)   
    reactor.run()

if __name__ == '__main__':
    main()