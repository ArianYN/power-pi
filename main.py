from api import API
from data_handler import DataHandler
from logger import Log
import psutil
import time
from models import *

class PowerPi:
    def __init__(self, dataIntervalSeconds):
        self.data = DataHandler()
        self.logger = Log()

        self.dataInterval = dataIntervalSeconds
        self.hasRead = False
        self.lastLoggedSecond = -1
        self.enableCharger = False

    def printUsage(self):
        process = psutil.Process()
        self.logger.log_divider()
        self.logger.log_info(f"Memory: {round(((process.memory_info().rss / 1024) / 1024), 1)} MB", True)
        self.logger.log_info(f"CPU: {process.cpu_percent()} %", True)

    def start(self):
        while True:
            elapsedTime = self.data.getLastGetTime()
            elapsedInt = int(elapsedTime)

            if elapsedInt % 50 == 0 and elapsedInt != self.lastLoggedSecond:
                self.logger.log_info(f"Fetching data in {self.dataInterval - elapsedInt} seconds", True)
                self.lastLoggedSecond = elapsedInt

            if elapsedTime > self.dataInterval:

                self.logger.log_divider()

                self.data.updatePowerConfig()

                pConf = self.data.getPowerConfig()

                priceUrl = self.data.getPriceUrl()
                rawData = None

                if priceUrl != '':
                    rawData = API.Get(priceUrl)
                else:
                    self.logger.log_info("Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                self.data.savePriceData(rawData)

                self.logger.log_info(f"Mode: {"Price-Based" if pConf.mode == PowerMode.PRICE_BASED else "Hour-Based"}", True)

                if pConf.mode == PowerMode.PRICE_BASED:
                    self.enableCharger = self.data.evaluate_PriceBased(rawData)

                elif pConf.mode == PowerMode.HOUR_BASED:
                    priceData = rawData['prices']
                    priceDataSorted = sorted(priceData, key=lambda item: item['price']['total'])
                    self.enableCharger = self.data.evaluate_HourBased(priceDataSorted)

                self.logger.log_info(f"Charger Enabled: {self.enableCharger}", True)

                self.printUsage()
                self.logger.log_divider()
            else:
                if not self.hasRead:
                    self.logger.log_info(f"Fetching data in {self.dataInterval - int(elapsedTime)} seconds", True)
                    self.hasRead = True

powerPi = PowerPi(300)
powerPi.start()