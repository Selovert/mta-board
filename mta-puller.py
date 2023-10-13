#!/usr/bin/env python

from nyct_gtfs import NYCTFeed
import datetime
import pickle
import os, sys
from math import floor
from time import sleep
from traceback import format_exception
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
fh = logging.FileHandler('/home/dietpi/Repos/mta-board/mta-board.log')
fh.setLevel(logging.WARNING)
logger.addHandler(fh)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception
class mtaPuller():
    def __init__(self, *args, **kwargs):
        super(mtaPuller, self).__init__(*args, **kwargs)
        self.apiKey = 'mb9p1Cod3H2EVsO9mPUwV6gZ6hxxFSYQ6L962J4F'
        self.arrivals = None
        self.dir = os.path.dirname(os.path.realpath(__file__))
    def run(self):
        while True:
            self.updateArrivals()
            self.writeArrivals()
            sleep(5)

    def updateArrivals(self):
        feed = NYCTFeed("L", api_key=self.apiKey)
        trains = feed.filter_trips(line_id=['L'], headed_for_stop_id=['L16N'], underway=True, travel_direction='N')

        self.arrivals = []

        if not len(trains): return None

        for t in trains:
            for s in t.stop_time_updates:
                if s.stop_id != 'L16N':
                    continue
                if s.arrival < datetime.datetime.now():
                    continue

                timeUntil:datetime.timedelta = s.arrival - datetime.datetime.now()
                self.arrivals.append({'ETA': s.arrival,
                                'Time until': f'{floor(timeUntil.seconds/60)} min {timeUntil.seconds % 60} sec',
                                'Next stop': t.stop_time_updates[0].stop_name,
                })
    
    def writeArrivals(self):
        with open(f'{self.dir}/mta-arrivals.cache', 'wb') as f:
            pickle.dump(self.arrivals, f)


if __name__ == "__main__":
    puller = mtaPuller()
    while True:
        try:
            puller.run()
        except Exception as ex:
            logging.error(''.join(format_exception(None, ex, ex.__traceback__)))
            continue