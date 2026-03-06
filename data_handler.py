from typing import List
from model import CompanySimple, CurrentPrice
from datetime import datetime, timezone

from logger import *

class DataHandler:
    def __init__ (self):
        pass

    def getCompanyId(self, company_data, selCompany):
        for company in company_data:
            name = company.get("name")
            
            if name == selCompany:
                products = company.get("products")
                id = products[0].get("id")
                return id

    def getPriceData(self, data):
        pass
        # use data from the priceUrl, to retrieve the current kr/kwh and return it. Float
