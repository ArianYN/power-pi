from enum import Enum
from dataclasses import dataclass

class PowerMode(Enum):
    PRICE_BASED = 1,
    HOUR_BASED = 2

@dataclass
class PowerConfig:
    mode: PowerMode
    company: str
    hours: int
    price: float