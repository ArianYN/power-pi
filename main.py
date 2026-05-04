from api import API
from data_handler import DataHandler
from logger import Log
import psutil
import time
from enum import Enum

class PowerMode(Enum):
    FLAT_PRICE = 1,
    HOURLY = 2

class PowerPi:
    def __init__(self, dataIntervalSeconds):
        self.data = DataHandler()
        self.logger = Log()

        self.dataInterval = dataIntervalSeconds
        self.hasRead = False
        self.lastLoggedSecond = -1
        self.enableCharger = False

        self.mode = PowerMode.HOURLY

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

                priceUrl = self.data.getPriceUrl()
                rawData = None

                if priceUrl != '':
                    rawData = API.Get(priceUrl)
                else:
                    self.logger.log_info("Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                self.data.savePriceData(rawData)

                if self.mode == PowerMode.FLAT_PRICE:
                    self.enableCharger = self.data.evaluate(rawData)
                    self.logger.log_info(f"Charger Enabled: {self.enableCharger}", True)
                elif self.mode == PowerMode.HOURLY:
                    priceData = rawData['prices']
                    priceDataSorted = sorted(priceData, key=lambda item: item['price']['total'])
                    print(priceDataSorted)

                self.printUsage()
                self.logger.log_divider()
            else:
                if not self.hasRead:
                    self.logger.log_info(f"Fetching data in {self.dataInterval - int(elapsedTime)} seconds", True)
                    self.hasRead = True

powerPi = PowerPi(300)
powerPi.start()