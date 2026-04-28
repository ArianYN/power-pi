from enum import Enum
from api import API
from logger import Log
from cache_handler import CacheHandler
import config as _config
import time
import json

class DataHandler:
    def __init__ (self):
        self.logger = Log()
        self.cache = CacheHandler()

        self.token = None
        
        self.companiesUrl = "https://stromligning.dk/api/companies?region=DK1&periodMonths=1"
        self.priceUrl = ""
        self.configUrl = f"http://10.133.51.103:9090/power-table?userId=auth0|{_config.USER_ID}"

        self.priceData_Filename = "priceCache"
        self.allCompanies_Filename = "companiesCache"

        self.priceData_GetTime = self.cache.getFileCacheTime(self.priceData_Filename)
        self.allCompanies_GetTime = self.cache.getFileCacheTime(self.allCompanies_Filename)

        self.confCompany = ""
        self.confMaxPrice = 0

        self.currentPrice = 1000

        self._fetchNewToken()
        self.updatePowerConfig()

    def __updatePriceUrl(self, newId):
        self.priceUrl = f"https://stromligning.dk/api/prices?productId={newId}&priceArea=DK1"

    def _fetchNewToken(self):
        res = API.PostXAdminKey(_config.HOSTNAME, _config.ADMIN_KEY, _config.SERVICE, _config.AUDIENCE, _config.SCOPES, _config.OLD_JTI)
        try:
            self.token = res['token']
            if self.token != None:
                self.logger.log_info("Fetched new token!")
                return True
        except:
            self.token = None
        self.logger.log_error("Failed to get new token...")
        return False

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
        return time.time() - self.priceData_GetTime
            
    def getPriceUrl(self):
        return self.priceUrl

    def savePriceData(self, data):
        self.cache.write(self.priceData_Filename, data)
        self.priceData_GetTime = self.cache.getFileCacheTime(self.priceData_Filename)
        return self.priceData_GetTime

    def getPricePerKwh(self, data):
        priceData = data['prices']
        priceData = priceData[0]['price']

        totalPrice = priceData['total']
        return totalPrice

    def evaluate(self, rawData):
        if rawData != 0 and rawData != None:
            self.currentPrice = self.getPricePerKwh(rawData)
            self.logger.log_info(f"Fetched Price: {str(round(self.currentPrice, 2))} kr/kwh", True)

        if self.currentPrice <= self.confMaxPrice:
            return True
        else:
            return False
        
    def _handleHttpError(self, errCode):
        match errCode:
            case 401:
                self.logger.log_warning(f"{errCode} Unauthorized - Token not valid - Fetching new...")
                if self._fetchNewToken():
                    self.updatePowerConfig()
            case 404:
                self.logger.log_error(f"{errCode} Not Found - Invalid URL?")
        
    def updatePowerConfig(self):
        elapsedTime = time.time() - self.allCompanies_GetTime
        if elapsedTime > 600:
            self.allCompanies = API.Get(self.companiesUrl)
            self.cache.write(self.allCompanies_Filename, self.allCompanies)
            self.allCompanies_GetTime = self.cache.getFileCacheTime(self.allCompanies_Filename)
        else:
            self.allCompanies = self.cache.read(self.allCompanies_Filename)
        
        if self.token == None:
            self.logger.log_warning("No Token - Trying to fetch new token...")
            if not self._fetchNewToken():
                return
            
        config = API.GetWithToken(self.configUrl, self.token)

        if type(config) is int:
            self._handleHttpError(config)
            return

        config = config[0]

        self.confCompany = config['company']
        self.confMaxPrice = config['price']

        self.logger.log_info(f'Fetched Company and Max Price: [{self.confCompany}, {self.confMaxPrice} kr/kwh]', True)

        compId = self.__getCompanyId()

        self.__updatePriceUrl(compId)