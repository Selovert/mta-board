#!/usr/bin/env python

from nyct_gtfs import NYCTFeed
import pickle, json
import os, sys, datetime
from math import floor
from time import sleep
from traceback import format_exception
import logging

from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
fh = logging.FileHandler(f'{os.path.dirname(os.path.realpath(__file__))}/mta-board.log')
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
        self.arrivingTrains: list[ArrivingTrain] = None
        self.dir = os.path.dirname(os.path.realpath(__file__))

        self.apiKey = 'mb9p1Cod3H2EVsO9mPUwV6gZ6hxxFSYQ6L962J4F'
        self.stationNameConfigFile = f'{self.dir}/stopNamesConfig.json'
        self.queryIntervalSec = 5 # time between calls in seconds

        self.line = 'L' # pick your line name. Mine is 'L' for the L train
        self.stopID = 'L16N' # ID for dekalb
        self.travelDirection = 'N' # only trains going north

        self.loadStationNames()

    def run(self):
        while True:
            self.updateArrivals()
            self.writeArrivals()
            sleep(self.queryIntervalSec)

    def updateArrivals(self):
        feed = NYCTFeed(self.line, api_key=self.apiKey)
        trains = feed.filter_trips(line_id=['L'], headed_for_stop_id=[self.stopID], underway=True, travel_direction=self.travelDirection)

        self.arrivingTrains = []

        if not len(trains): return None

        for t in trains:
            pass
            for s in t.stop_time_updates:
                if s.stop_id != self.stopID: # if the stop is not dekalb
                    continue
                if s.arrival < datetime.datetime.now(): # if the train already passed
                    continue

                timeUntil:datetime.timedelta = s.arrival - datetime.datetime.now()
                trainMoving = True if t.location_status == 'IN_TRANSIT_TO' else False
                stopsRemaining = [s.stop_id for s in t.stop_time_updates].index(self.stopID) + 1
                nextStop = t.stop_time_updates[0].stop_name
                if nextStop in self.stationNameMap.keys():
                    nextStop = self.stationNameMap[nextStop]

                trainDelay = t.has_delay_alert
                # lineAlert = True if 'L' in feed.trip_replacement_periods.keys() else False
                lineAlert = False
                
                trainInfo = ArrivingTrain(eta=s.arrival,
                                  timeUntil=timeUntil,
                                  nextStop=nextStop,
                                  stopsRemaining=stopsRemaining,
                                  trainMoving=trainMoving,
                                  trainDelay=trainDelay,
                                  lineAlert=lineAlert)
                self.arrivingTrains.append(trainInfo)
    
    def writeArrivals(self):
        with open(f'{self.dir}/mta-arrivals.cache', 'wb') as f:
            pickle.dump(self.arrivingTrains, f)

    def loadStationNames(self):
        self.stationNameMap = {}

        if not os.path.isfile(self.stationNameConfigFile):
            return None

        with open(self.stationNameConfigFile) as f:
            raw_json:dict = json.load(f)
        
        if self.line not in raw_json.keys():
            return None

        self.stationNameMap:dict = raw_json[self.line]


@dataclass
class ArrivingTrain:
    eta: datetime.datetime
    timeUntil: datetime.timedelta = field(init=True, repr=False)
    timeUntilStr: str = field(init=False, repr=True)
    nextStop: str
    stopsRemaining: int
    trainMoving:bool
    trainDelay:bool
    lineAlert:bool

    def __post_init__(self):
        self.timeUntilStr = f'{floor(self.timeUntil.seconds/60)} min {self.timeUntil.seconds % 60} sec'



if __name__ == "__main__":
    puller = mtaPuller()
    while True:
        try:
            puller.run()
        except Exception as ex:
            logging.error(''.join(format_exception(None, ex, ex.__traceback__)))
            continue