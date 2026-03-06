from cache_handler import CacheHandler
from request_handler import RequestHandler
from data_handler import DataHandler
from logger import *
import time

cHandler = CacheHandler()
rHandler = RequestHandler()
dHandler = DataHandler()

selectedCompany = "NRGi"
selectedMaxPrice = 1.2

rawData = 0

lastGetTime = cHandler.getLastCacheTime()

compData = rHandler.get("https://stromligning.dk/api/companies?region=DK1&periodMonths=1")
compId = dHandler.getCompanyId(compData, selectedCompany)

priceUrl = f"https://stromligning.dk/api/prices?productId={compId}&priceArea=DK1"

while True:
    time.sleep(1)
    elapsedTime = time.time() - lastGetTime

    log_info(f"Time Elapsed {elapsedTime}")

    if elapsedTime > 300: # 5 minutes has passed
        rawData = rHandler.get(priceUrl)

        cHandler.write(rawData)
        lastGetTime = cHandler.getLastCacheTime()
    else:
        rawData = cHandler.read()
        if rawData == "No Data":
            rawData = 0
            log_error("No data from cache...")

    if rawData != 0 and rawData != None:
        parsedData = dHandler.getPriceData(rawData)

    

