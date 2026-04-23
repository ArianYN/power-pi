from cache_handler import CacheHandler
from api import API
from data_handler import DataHandler
from logger import Log
import time

class PowerPi:
    def __init__(self, dataIntervalSeconds):
        self.data = DataHandler()
        self.logger = Log()

        self.dataInterval = dataIntervalSeconds
        self.hasRead = False
        self.lastLoggedSecond = -1
        self.enableCharger = False

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
                self.rawData = API.Get(self.data.getPriceUrl())
                self.lastGetTime = self.data.saveData(self.rawData)
                self.enableCharger = self.data.shouldEnableCharger(self.rawData)

                self.logger.log_info(f"Charger Enabled: {self.enableCharger}", True)
                self.logger.log_divider()
            else:
                if not self.hasRead:
                    self.logger.log_info(f"Fetching data in {self.dataInterval - int(elapsedTime)} seconds", True)
                    self.hasRead = True

powerPi = PowerPi(300)
powerPi.start()