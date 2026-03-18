from cache_handler import CacheHandler
from api_handler import APIHandler
from data_handler import DataHandler
from logger import Log
import time

cHandler = CacheHandler()
aHandler = APIHandler()
dHandler = DataHandler()
logger = Log()

selectedCompany = "NRGi" # aHandler.getSelectedCompany()
selectedMaxPrice = 1.5 #aHandler.getSelectedMaxPrice

lastPrice = 100
currentPrice = 100

enableCharger = False
lastEnableCharger = False

rawData = 0

lastGetTime = cHandler.getLastCacheTime()

compData = aHandler.get("https://stromligning.dk/api/companies?region=DK1&periodMonths=1")
compId = dHandler.getCompanyId(compData, selectedCompany)

priceUrl = f"https://stromligning.dk/api/prices?productId={compId}&priceArea=DK1"

while True:
    time.sleep(1)
    elapsedTime = time.time() - lastGetTime

    elapsedInt = int(elapsedTime)

    if elapsedInt % 15 == 0:
        logger.log_info(f"Fetching Data in {300 - elapsedInt} seconds", True)

    if elapsedTime > 300: # 5 minutes has passed
        rawData = aHandler.get(priceUrl)

        cHandler.write(rawData)
        lastGetTime = cHandler.getLastCacheTime()

    else:
        rawData = cHandler.read()
        if rawData == "No Data":
            rawData = 0
            logger.log_error("No data from cache...")

    if rawData != 0 and rawData != None:
        currentPrice = dHandler.getPricePerKwh(rawData)
        
    if currentPrice < selectedMaxPrice:
        enableCharger = True
    else:
        enableCharger = False

    if lastEnableCharger != enableCharger:
        logger.log_info(f"Charger Enabled: {enableCharger}", True)

    if lastPrice != currentPrice:
        logger.log_info(f"Fetched New Price: {currentPrice} kr/kwh", True)
    
    lastPrice = currentPrice
    lastEnableCharger = enableCharger

    

