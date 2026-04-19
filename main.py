from cache_handler import CacheHandler
from api_handler import APIHandler
from data_handler import DataHandler
from logger import Log
import time

class PowerPi:
    def __init__(self, dataIntervalSeconds):
        self.cache = CacheHandler()
        self.api = APIHandler()
        self.data = DataHandler()
        self.logger = Log()

        self.hasRead = False

        self.selectedCompany = "NRGi" # self.__getSelectedCompany()
        self.selectedMaxPrice = 1.5 # self.__getSelectedPrice()

        self.currentPrice = 300
        self.dataInterval = dataIntervalSeconds

        self.enableCharger = False
        self.rawData = 0
        self.lastGetTime = self.cache.getLastCacheTime()

        self.companies = self.api.get("https://stromligning.dk/api/companies?region=DK1&periodMonths=1")
        self.companyId = self.data.getCompanyId(self.companies, self.selectedCompany)
        self.priceUrl = f"https://stromligning.dk/api/prices?productId={self.companyId}&priceArea=DK1"

    def __getSelectedCompany(self):
        pass

    def __getSelectedPrice(self):
        pass
    
    def __evaluateData(self):
        if self.rawData != 0 and self.rawData != None:
            self.currentPrice = self.data.getPricePerKwh(self.rawData)
            self.logger.log_info(f"Fetched Price: {self.currentPrice} kr/kwh", True)

        if self.currentPrice < self.selectedMaxPrice:
            self.enableCharger = True
        else:
            self.enableCharger = False

        self.logger.log_info(f"Charger Enabled: {self.enableCharger}", True)

    def __getTime(self):
        elapsedTime = time.time() - self.lastGetTime
        elapsedInt = int(elapsedTime)

        if elapsedInt % 15 == 0:
            self.logger.log_info(f"Fetching Data in {self.dataInterval - elapsedInt} seconds", True)

        return elapsedTime
    
    def __cacheData(self):
        self.cache.write(self.rawData)
        self.lastGetTime = self.cache.getLastCacheTime()

    def start(self):
        while True:
            elapsedTime = self.__getTime()

            if elapsedTime > self.dataInterval:
                self.rawData = self.api.get(self.priceUrl)
                self.__cacheData()
                self.__evaluateData()
            else:
                if not self.hasRead:
                    self.logger.log_info(f"Fetching data in {self.dataInterval - int(elapsedTime)} seconds", True)
                    self.hasRead = True


powerPi = PowerPi(300)
powerPi.start()