from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class CurrentPrice(BaseModel):
    productId: str
    productName: str
    priceName: str
    amount: Optional[float]

class CompanySimple(BaseModel):
    id: str
    name: str
    image: Optional[str]
    currentPrices: list[CurrentPrice]