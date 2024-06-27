from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class MonthBase(BaseModel):
    month_year = datetime
    bankroll = Decimal
    unit_size = Decimal

class MonthCreate(MonthBase):
    pass

class Month(MonthBase):
    singles: list['Single'] = []

    class Config:
        orm_mode = True

class SingleBase(BaseModel):
    result = str
    pick = str
    sport = str
    units = Decimal
    odds = Decimal
    timestamp = Decimal
    profit = Decimal
    net_profit = Decimal
    wager = Decimal
    month_bankroll = datetime

class SingleCreate(SingleBase):
    pass

class Single(SingleBase):
    id = int