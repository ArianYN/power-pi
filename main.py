from cache_handler import CacheHandler
from api_handler import APIHandler
from data_handler import DataHandler
from logger import *
import time

cHandler = CacheHandler()
aHandler = APIHandler()
dHandler = DataHandler()

selectedCompany = "NRGi" # aHandler.getSelectedCompany()
selectedMaxPrice = 1.6 #aHandler.getSelectedMaxPrice

currentPrice = 100
enableCharger = False

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
        log_info(f"Fetching Data in {300 - elapsedInt} seconds")
        time.sleep(1)

    if elapsedTime > 300: # 5 minutes has passed
        rawData = aHandler.get(priceUrl)

        cHandler.write(rawData)
        lastGetTime = cHandler.getLastCacheTime()

        if rawData != 0 and rawData != None:
            currentPrice = dHandler.getPricePerKwh(rawData)
            log_info(f"Fetched Price: {currentPrice}")

        if currentPrice < selectedMaxPrice:
            enableCharger = True
        else:
            enableCharger = False

        log_info(f"Charger Enabled: {enableCharger}")
    else:
        rawData = cHandler.read()
        if rawData == "No Data":
            rawData = 0
            log_error("No data from cache...")

    

