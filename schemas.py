from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

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
    profit: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    wager: Optional[Decimal] = None
    month_year: Optional[str] = None

class SingleCreate(SingleBase):
    month_id: Optional[int] = None
    month: Optional[MonthCreate] = None

class Single(SingleBase):
    id: int

    class Config:
        orm_mode = True