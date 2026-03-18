from typing import List
from model import CompanySimple, CurrentPrice
from datetime import datetime, timezone

class DataHandler:
    def __init__ (self):
        pass

    def getCompanyId(self, company_data, selCompany):
        for company in company_data:
            name = company["name"]
            
            if name == selCompany:
                products = company["products"]
                id = products[0]["id"]
                return id

    def getPricePerKwh(self, data):
        priceData = data['prices']
        priceData = priceData[0]['price']

        totalPrice = priceData['total']
        return totalPrice
