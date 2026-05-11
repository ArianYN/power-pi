from enum import Enum
from api import API
from logger import Log
from redis_cache import RedisCache
import config as _config
import time
import datetime
from requests import Response
from models import *

class DataHandler:
    def __init__ (self):
        self.logger = Log()
        self.rCache = RedisCache()

        self.token = None
        
        self.companiesUrl = "https://stromligning.dk/api/companies?region=DK1&periodMonths=1"
        self.priceUrl = ""
        self.configUrl = f"https://powerpi.mercantec.tech/power-table?userId=auth0|{_config.USER_ID}"
        self.chargingUrl = f"https://powerpi.mercantec.tech/charging?userId=auth0|{_config.USER_ID}"

        self.priceData_Filename = "priceCache"
        self.allCompanies_Filename = "companiesCache"

        self.priceData_GetTime = self.rCache.getLastCacheTime(self.priceData_Filename)
        self.allCompanies_GetTime = self.rCache.getLastCacheTime(self.allCompanies_Filename)

        self.powerConfig = PowerConfig(None, None, None, None)

        self.currentPrice = 1000

        self._fetchNewToken()
        self.updatePowerConfig()

    def __updatePriceUrl(self, newId):
        today = datetime.date.today()
        todayStr = today.strftime("%Y-%m-%d")
        self.priceUrl = f"https://stromligning.dk/api/prices?from={todayStr}&productId={newId}&priceArea=DK1"

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
            
            if name == self.powerConfig.company:
                products = company["products"]
                if len(products) == 0:
                    self.logger.log_error("No Products for Company - Returning empty string")
                    return ""
                id = products[0]["id"]
                return id
            
    def getLastGetTime(self):
        return int(time.time()) - self.priceData_GetTime
            
    def getPriceUrl(self):
        return self.priceUrl
    
    def getPowerConfig(self):
        return self.powerConfig

    def savePriceData(self, data):
        self.rCache.write(self.priceData_Filename, data)
        self.priceData_GetTime = self.rCache.getLastCacheTime(self.priceData_Filename)
        return self.priceData_GetTime

    def getPricePerKwh(self, data):
        priceData = data['prices']
        priceData = priceData[0]['price']

        totalPrice = priceData['total']
        return totalPrice

    def evaluate_PriceBased(self, rawData):
        if rawData != 0 and rawData != None:
            self.currentPrice = self.getPricePerKwh(rawData)
            self.logger.log_info(f"Fetched Price: {str(round(self.currentPrice, 2))} kr/kwh", True)

        if self.currentPrice <= self.powerConfig.price:
            return True
        else:
            return False
        
    def evaluate_HourBased(self, sortedData):
        quarters = 4 * self.powerConfig.hours
        
        selectedData = sortedData[:quarters]
    
        uniqueHours = set()
        
        tzOffsetHours = 0
        if selectedData:
            try:
                utcDateStr = selectedData[0].get('date')
                localDateStr = selectedData[0].get('localDate')
                if utcDateStr and localDateStr:
                    utcDt = datetime.datetime.fromisoformat(utcDateStr.replace('Z', '+00:00'))
                    localDt = datetime.datetime.fromisoformat(localDateStr)
                    tzOffsetHours = (localDt.hour - utcDt.hour) % 24
            except Exception as e:
                self.logger.log_error(f"Failed to calculate timezone offset: {str(e)}", True)
        
        currentHourUtc = datetime.datetime.utcnow().hour
        currentHour = (currentHourUtc + tzOffsetHours) % 24
        
        for dataPoint in selectedData:
            if len(uniqueHours) >= self.powerConfig.hours:
                break
            try:
                dateStr = dataPoint.get('localDate')
                
                if dateStr:
                    dt = datetime.datetime.fromisoformat(dateStr)
                    uniqueHours.add(dt.hour)
            except Exception as e:
                self.logger.log_error(f"Failed to parse timestamp: {dataPoint.get('localDate')} - {str(e)}", True)
        
        result = currentHour in uniqueHours
        self.logger.log_info(f"Hour-Based Evaluation: Current hour: {currentHour} - Data Hours:{sorted(uniqueHours)}", True)
        return result
    
    def updateDatabaseFlag(self, charging):
        body = {
            "charging": charging
        }

        if self.token == None:
            self.logger.log_warning("No Token - Trying to fetch new token...")
            if not self._fetchNewToken():
                return
            
        response = API.PatchWithToken(self.chargingUrl, self.token, body)

        if response.status_code == 200 or response.status_code == 201:
            self.logger.log_info(f"Set Charging Flag: {charging}")
        else:
            self._handleHttpError(response)
        
    def _handleHttpError(self, response: Response):
        errCode = response.status_code
        reason = response.reason
        description = response.text
        
        if errCode == 401:
            self.logger.log_warning(f"{errCode} {reason} - {description} - Fetching new...", True)
            if self._fetchNewToken():
                self.updatePowerConfig()
        elif errCode != 201 and errCode != 200:
            self.logger.log_error(f"{errCode} {reason} - {description}", True)
    
    def updatePowerConfig(self):
        elapsedTime = int(time.time()) - self.allCompanies_GetTime
        
        if elapsedTime > 600:
            self.allCompanies = API.Get(self.companiesUrl)
            if self.allCompanies != None:
                self.rCache.write(self.allCompanies_Filename, self.allCompanies)
                self.allCompanies_GetTime = self.rCache.getLastCacheTime(self.allCompanies_Filename)
            else:
                self.logger.log_warning("Could not retrieve companies...", True)
        else:
            self.allCompanies = self.rCache.readAll(self.allCompanies_Filename)
        
        if self.token == None:
            self.logger.log_warning("No Token - Trying to fetch new token...")
            if not self._fetchNewToken():
                return
            
        config = API.GetWithToken(self.configUrl, self.token)

        if not isinstance(config, list):
            self._handleHttpError(config)
            return

        config = config[0]

        mode = config['selectionMode']
        self.powerConfig.company = config['company']
        self.powerConfig.hours = config['numberOfHours']
        self.powerConfig.price = config['price']

        if "hour" in mode:
            self.powerConfig.mode = PowerMode.HOUR_BASED
        elif "price" in mode:
            self.powerConfig.mode = PowerMode.PRICE_BASED

        self.logger.log_info(f'Fetched Config: SelectionMode: {self.powerConfig.mode} - Company: {self.powerConfig.company} - Hours: {self.powerConfig.hours} - MaxPrice: {self.powerConfig.price}', True)

        compId = self.__getCompanyId()

        self.__updatePriceUrl(compId)
