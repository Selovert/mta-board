#!/usr/bin/env python
import time
import sys
import os
import datetime
import time
import subprocess
import pickle

from math import floor

sys.path.append("rpi-rgb-led-matrix/bindings/python")
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics
from PIL import Image
from PIL import ImageDraw
from nyct_gtfs import NYCTFeed

class matrixBoard():
    def __init__(self, *args, **kwargs):
        super(matrixBoard, self).__init__(*args, **kwargs)
        # Configuration for the matrix
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.brightness = 60
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
        options.gpio_slowdown = 0
        options.pwm_lsb_nanoseconds = 130
        # options.pwm_dither_bits = 2
        # options.limit_refresh_rate_hz = 120
        options.show_refresh_rate = 1

        self.matrix = RGBMatrix(options = options)
        self.dir = os.path.dirname(os.path.realpath(__file__))

    def run(self):
        self.startTime = datetime.datetime.now()
        self.font = graphics.Font()
        self.font.LoadFont("rpi-rgb-led-matrix/fonts/5x7.bdf")
        self.canvas = self.matrix.CreateFrameCanvas()
        self.imgCanvas = self.matrix.CreateFrameCanvas()
        self.imagesLoaded = False
        self.logo = Image.open(f'{self.dir}/L_logo.png').convert('RGB')
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
    board.run()