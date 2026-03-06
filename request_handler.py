import requests
from datetime import datetime, timezone
from typing import List
from model import CompanySimple, CurrentPrice

from logger import *


class RequestHandler:
    def __init__(self):
        pass
    
    def get(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.json()