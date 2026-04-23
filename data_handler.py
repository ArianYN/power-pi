from enum import Enum
from api import API
from logger import Log
from cache_handler import CacheHandler
import config
import time

class DataHandler:
    def __init__ (self):
        self.logger = Log()
        self.cache = CacheHandler()

        self.companiesUrl = "https://stromligning.dk/api/companies?region=DK1&periodMonths=1"
        self.priceUrl = ""
        self.configUrl = f"http://10.133.51.103:9090/power-table?userId=auth0|{config.USER_ID}"

        self.confCompany = ""
        self.confMaxPrice = 0

        self.powerPrice = 1000

        self.allCompanies = API.Get(self.companiesUrl)
        self.allCompanies_GetTime = 0

        self.updatePowerConfig()

        self.data_GetTime = self.cache.getLastCacheTime()

    def __updatePriceUrl(self, newId):
        self.priceUrl = f"https://stromligning.dk/api/prices?productId={newId}&priceArea=DK1"

    def __getCompanyId(self):
        for company in self.allCompanies:
            name = company["name"]
            
            if name == self.confCompany:
                products = company["products"]
                if len(products) == 0:
                    self.logger.log_error("No Products for Company - Returning empty string")
                    return ""
                id = products[0]["id"]
                return id
            
    def getLastGetTime(self):
        return time.time() - self.data_GetTime
            
    def getPriceUrl(self):
        return self.priceUrl

    def saveData(self, data):
        self.cache.write(data)
        self.data_GetTime = self.cache.getLastCacheTime()
        return self.data_GetTime

    def getPricePerKwh(self, data):
        priceData = data['prices']
        priceData = priceData[0]['price']

        totalPrice = priceData['total']
        return totalPrice

    def shouldEnableCharger(self, rawData):
        if rawData != 0 and rawData != None:
            self.powerPrice = self.getPricePerKwh(rawData)
            self.logger.log_info(f"Fetched Price: {str(round(self.powerPrice, 2))} kr/kwh", True)

        if self.powerPrice < self.confMaxPrice:
            return True
        else:
            return False
        
    def updatePowerConfig(self):
        if (time.time() - self.allCompanies_GetTime) > 600:
            self.allCompanies = API.Get(self.companiesUrl)
            self.allCompanies_GetTime = time.time()
        
        config = API.Get(self.configUrl)[0]

        self.confCompany = config['company']
        self.confMaxPrice = config['price']

        self.logger.log_info(f'Fetched Company and Max Price: [{self.confCompany}, {self.confMaxPrice} kr/kwh]', True)

        compId = self.__getCompanyId()

        self.__updatePriceUrl(compId)