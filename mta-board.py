#!/usr/bin/env python
import time
import sys
import os
import datetime
import time
import subprocess
import pickle

sys.path.append("/home/dietpi/Repos/mta-board/rpi-rgb-led-matrix/bindings/python")
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics
from PIL import Image
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

class matrixBoard():
    def __init__(self, *args, **kwargs):
        # Configuration for the matrix
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.brightness = 60
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
        options.gpio_slowdown = 3
        # options.pwm_lsb_nanoseconds = 130
        options.limit_refresh_rate_hz = 160
        options.show_refresh_rate = 0
        
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.logo = Image.open(f'{self.dir}/L_logo.png').convert('RGB')

        self.matrix = RGBMatrix(options = options)
        self.runTime = datetime.timedelta(0)

    def run(self):
        self.startTime = datetime.datetime.now()
        self.font = graphics.Font()
        self.font.LoadFont("/home/dietpi/Repos/mta-board/rpi-rgb-led-matrix/fonts/5x7.bdf")
        self.canvas = self.matrix.CreateFrameCanvas()
        self.imgCanvas = self.matrix.CreateFrameCanvas()
        self.imagesLoaded = False
        while True:
            self.readArrivals()
            self.runTime = datetime.datetime.now() - self.startTime
            self.canvas.Clear()
            if self.runTime.seconds < 2:
                self.showIP()
            else:
                if len(self.arrivals):
                    self.showTrains()
            time.sleep(0.1)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
    
    def showIP(self):
        rawIP: str = subprocess.check_output(['hostname', '-I'], encoding='UTF-8')
        ip = rawIP.split(' ')[0]
        graphics.DrawText(self.canvas, self.font, 0, 6, graphics.Color(255, 255, 255), ip)

    def readArrivals(self):
        try:
            with open(f'{self.dir}/mta-arrivals.cache', 'rb') as f:
                self.arrivals: list = pickle.load(f)
        except:
            return None

    def showTrains(self):
        
        
        # first train
        # if not self.imagesLoaded:
        self.canvas.SetImage(self.logo, 0, 1)
        graphics.DrawText(self.canvas, self.font, 10, 7, graphics.Color(255, 255, 255), self.arrivals[0]['Next stop'])
        graphics.DrawText(self.canvas, self.font, 0, 15, graphics.Color(255, 255, 255), self.arrivals[0]['Time until'])

        if len(self.arrivals) < 2: return None
        # second train
        # if not self.imagesLoaded:
        self.canvas.SetImage(self.logo, 0, 16)
        graphics.DrawText(self.canvas, self.font, 10, 23, graphics.Color(255, 255, 255), self.arrivals[1]['Next stop'])
        graphics.DrawText(self.canvas, self.font, 0, 31, graphics.Color(255, 255, 255), self.arrivals[1]['Time until'])

        self.imagesLoaded = True

if __name__ == "__main__":
    board = matrixBoard()
    while True:
        try:
            board.run()
        except Exception as ex:
            logging.error(''.join(format_exception(None, ex, ex.__traceback__)))
            continue