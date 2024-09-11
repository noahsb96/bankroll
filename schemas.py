from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List

class MonthBase(BaseModel):
    month_year: datetime
    bankroll: Decimal
    unit_size: Decimal

class MonthCreate(MonthBase):
    pass

class Month(MonthBase):
    id: int
    singles: List['Single'] = []

    class Config:
        orm_mode = True

class SingleBase(BaseModel):
    result: str
    pick: str
    sport: str
    units: Decimal
    odds: Decimal
    timestamp: datetime
    profit: Decimal
    net_profit: Decimal
    wager: Decimal
    month_id: int

class SingleCreate(SingleBase):
    pass

class Single(SingleBase):
    id: int

    class Config:
        orm_mode = True