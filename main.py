from fastapi import FastAPI
app = FastAPI()
from pydantic import BaseModel, validator
from fastapi.encoders import jsonable_encoder
from typing import Optional, Dict, Any
from datetime import datetime, date
import locale
from re import sub
from decimal import Decimal
locale.setlocale(locale.LC_ALL, 'C')

class Month(BaseModel):
    bankroll: float
    month_year: datetime
    unit_size: float

    @validator('month_year', pre=True, always=True)
    def parse_date_string(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%m/%Y')
            except ValueError:
                raise ValueError("timestamp must be in the format MM/YYYY")
        return value
    
    def dict(self, **kwargs):
        dict_data = super().model_dump(**kwargs)
        if self.month_year:
            dict_data['month_year'] = self.month_year.strftime('%m/%Y')
        return dict_data

    def json(self, **kwargs):
        return super().model_dump_json(**kwargs)
    
class Single(BaseModel):
    result: str
    pick: str 
    sport: str
    units: float
    odds: float
    timestamp: Optional[datetime] = None
    profit_number: Optional[float] = None
    wager: Optional[float] = None
    profit: Optional[str] = None
    month_bankroll: Month

    @validator('timestamp', pre=True, always=True)
    def parse_date_string(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%m/%d/%Y')
            except ValueError:
                raise ValueError("timestamp must be in the format MM/DD/YYYY")
        return value
    
    def dict(self, **kwargs):
        dict_data = super().model_dump(**kwargs)
        if self.timestamp:
            dict_data['timestamp'] = self.timestamp.strftime('%m/%d/%Y')
        return dict_data

    def json(self, **kwargs):
        return super().model_dump_json(**kwargs)
    
class Record(BaseModel):
    wins: int
    losses: int
    pushes: int
    win_percentage: int

class BettingSummary(BaseModel):
    start_date: date
    end_date: date
    total_profit: Decimal
    unit_profit: Decimal
    avg_odds: Decimal
    growth: int
    win_rate: int
    roi: int
    units_spent: float
    money_spent: float
    units_won: float
    winnings: float
    net_profit: float
    wins: int
    losses: int
    pushes: int
    sports: Dict[str, Record]

singles_db: Dict[int, Single] = {}
next_id = 0
months_db: Dict[str, Month] = {}

def format_currency(amount):
    if amount >= 0:
         return '${:,.2f}'.format(amount)
    else:
        return '-${:,.2f}'.format(abs(amount))

def format_decimal(amount):
    return Decimal(sub(r'[^\d\-.]', '', amount))

def profit(single: Any) -> None:
    unit_size = single.month_bankroll.unit_size
    wager = unit_size * single.units
    if single.result == "won":
        single.wager = wager
        single.profit_number = single.odds * wager
    elif single.result == "lost":
        single.wager = wager
        single.profit_number = -wager
    elif single.result == "push":
        single.wager = wager
        single.profit_number = 0
    else:
        return {"Message: Incorrect Result Entered. Enter Win, Loss, Or Push"}
    single.profit = format_currency(single.profit_number)

def update_months_db(month: Month):
    month_str = month.month_year.strftime('%m/%Y')
    if month_str not in months_db:
        months_db[month_str] = month
    return months_db[month_str]

@app.get("/singles/daily")
async def get_daily_bets():
    today = datetime.now().date()
    daily_bets = [single for single in singles_db.values() if single.timestamp.date() == today]
    return daily_bets

@app.get("/singles/by_date/{date}")
async def get_bets_by_date(date: date):
    bets_on_date = [single for single in singles_db.values() if single.timestamp.date() == date]
    return bets_on_date

@app.get("/singles/{single_id}")
async def read_single_bet(single_id: int):
    single = singles_db[single_id]
    if single is None:
        return {"message": "Item not Found"}
    return single

@app.get("/singles/")
async def read_single():
    return singles_db

@app.post("/singles/")
async def create_single(single: Single):
    global next_id
    single.timestamp = datetime.now() if single.timestamp is None else single.timestamp
    profit(single)
    month_instance = update_months_db(single.month_bankroll)
    single.month_bankroll = month_instance
    single.wager = format_currency(single.wager)
    singles_db[next_id] = single
    next_id += 1
    return single

@app.put("/singles/{single_id}", response_model=Single)
async def update_single(single_id: int, single: Single):
    singles_db[single_id] = single
    profit(single)
    return single

@app.delete("/singles/{single_id}")
async def delete_single(single_id: int):
        del singles_db[single_id]
        return {"message": "Item deleted successfully"}

@app.get("/betting_summary/{start_date}/{end_date}")
async def get_betting_summary(start_date: date, end_date: date):
    betting_summary = BettingSummary(
        start_date=start_date,
        end_date=end_date,
        total_profit=0.0,
        unit_profit=0.0,
        avg_odds=0.0,
        growth=0,
        win_rate=0,
        roi=0,
        units_spent=0.0,
        money_spent=0.0,
        units_won=0.0,
        winnings=0.0,
        net_profit=0.0,
        wins=0,
        losses=0,
        pushes=0,
        sports={}
    )

    bets_in_date_range = [
        single for single in singles_db.values() if start_date <= single.timestamp.date() and single.timestamp.date() <= end_date
    ]

    added_odds = 0

    for bet in bets_in_date_range:
        sport = bet.sport
        if sport not in betting_summary.sports:
            betting_summary.sports[sport] = Record(wins=0, losses=0, pushes=0, win_percentage=0)
        betting_summary.total_profit += format_decimal(bet.profit)
        betting_summary.unit_profit += format_decimal(bet.profit_number) / bet.month_bankroll.unit_size
        added_odds += bet.odds
    
    betting_summary.total_profit = format_currency(betting_summary.total_profit)
    betting_summary.avg_odds = round(added_odds/len(bets_in_date_range), 2)
    return betting_summary