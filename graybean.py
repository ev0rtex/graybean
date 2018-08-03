#!/usr/bin/env python3
""" Monitor tube stats for a given beanstalk server and report them to graylog

Example:
    $ graybean.py \
          --beanstalk bean3.ksl.com:11300 \
          --graylog graylog.deseretdigital.com:11211 \
          --tube default
"""
import os.path as osp
import sys
import time
import argparse
import logging

import greenstalk as gs
from pygelf import GelfUdpHandler, GelfTcpHandler


def merged(*dicts):
    r = {}
    for d in dicts:
        r.update(d)
    return r


def main():
    """
    Stats reporting tool to send beastalk tube stats to graylog
    """
    #
    # Set up arg parsing and gather CLI args
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--beanstalk", type=str, help="beanstalk server and port")
    parser.add_argument("-g", "--graylog", type=str,
                        help="graylog server and port for GELF input")
    parser.add_argument("-t", "--tubes", type=str, default="default",
                        help="list of tubes to watch (comma-separated)")
    parser.add_argument("-u", "--udp", action="store_true",
                        help="use UDP for GELF graylog connection (TCP is default)")
    args = parser.parse_args()

    if not args.beanstalk:
        print("You need to provide a beanstalk server to connect to")
        sys.exit(1)
    else:
        beanstalk = {
            'host': None,
            'port': None
        }
        beanstalk['host'], _, beanstalk['port'] = args.beanstalk.partition(':')

    if not args.graylog:
        print("You need to provide a graylog server to send data to")
        sys.exit(1)
    else:
        graylog = {
            'host': None,
            'port': None
        }
        graylog['host'], _, graylog['port'] = args.graylog.partition(':')

    if not args.tubes:
        print("You need to provide one or more tubes to monitor stats for")
        sys.exit(1)

    #
    # Set up logger
    logging.basicConfig(level=logging.INFO)
    gelf_handler = (GelfUdpHandler if args.udp else GelfTcpHandler)(
            host=graylog.get('host', '127.0.0.1'),
            port=int(graylog.get('port', '12201')),
            include_extra_fields=True
        )
    logger = logging.getLogger()
    logger.handlers = []
    logger.addHandler(gelf_handler)

    # Default record info
    logging_defaults = {
        'name': 'graybean',
        'level': logging.getLevelName(logging.INFO),
        'levelno': logging.INFO,
        'pathname': osp.realpath(__file__),
        'msg': '',
        'args': None,
        'exc_info': None
    }

    # Get connected
    queue = gs.Client(**beanstalk)
    tubes = [x.strip() for x in args.tubes.split(',')]
    print("Collecting stats for tube{} '{}' every 5 seconds...".format('s' if len(tubes) > 1 else '', ', '.join(tubes)))
    while True:
        try:
            for tube in tubes:
                record = merged(logging_defaults, {
                        'msg': "Stats for tube '{}' from '{}'".format(tube,
                                                                      beanstalk['host']),
                        'tube': tube
                    },
                    queue.stats_tube(tube)
                )
                logger.handle(logging.makeLogRecord(record))

            # Sleep for 5s
            time.sleep(5)

        except KeyboardInterrupt:
            print("\nExiting gracefully")
            sys.exit(0)


if __name__ == '__main__':
    main()
