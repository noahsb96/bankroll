from fastapi import FastAPI, HTTPException
app = FastAPI()
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
import locale
from re import sub
from decimal import Decimal
locale.setlocale(locale.LC_ALL, 'C')

class Month(BaseModel):
    bankroll: Decimal
    month_year: datetime
    unit_size: Decimal

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
    units: Decimal
    odds: Decimal
    timestamp: Optional[datetime] = None
    profit_number: Optional[Decimal] = None
    net_profit_number: Optional[Decimal] = None
    wager: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
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
    units_spent: Decimal
    money_spent: Decimal
    units_won: Decimal
    winnings: Decimal
    net_profit: Decimal
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
    single.net_profit_number = single.profit_number - single.wager
    single.net_profit = format_currency(single.net_profit_number)
    single.profit = format_currency(single.profit_number)

def update_months_db(month: Month):
    month_str = month.month_year.strftime('%m/%Y')
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

@app.get("/monthly/bankroll/")
async def read_bankrolls():
    return months_db

@app.get("/monthly/bankroll/{month_date}")
async def read_month_bankroll(month_date: str):
    print(f"Received month_date: {month_date}")
    month_datetime = datetime.strptime(month_date, '%m-%Y')
    month_key = month_datetime.strftime('%m/%Y')
    bankroll = months_db.get(month_key)
    if bankroll is None:
        {"message": "Item not Found"}
    return bankroll

@app.post("/singles/")
async def create_single(single: Single):
    global next_id
    single.timestamp = datetime.now() if single.timestamp is None else single.timestamp
    profit(single)
    month_key = single.month_bankroll.month_year.strftime('%m/%Y')
    if month_key not in months_db:
        month_instance = update_months_db(single.month_bankroll)
    else:
        month_instance = months_db[month_key]
    single.month_bankroll = month_instance
    single.wager = format_currency(single.wager)
    singles_db[next_id] = single
    next_id += 1
    return single

@app.post("/monthly/bankroll/")
async def create_bankroll(month: Month):
    month_str = month.month_year.strftime('%m/%Y')
    if month_str not in months_db:
        update_months_db(month)
    else:
        return {"Message: Month already entered. Enter new month or update month"}

@app.put("/singles/{single_id}", response_model=Single)
async def update_single(single_id: int, single: Single):
    singles_db[single_id] = single
    profit(single)
    return single

@app.put("/monthly/bankroll/{month_date}", response_model=Month)
async def update_month(month_date: str, month: Month):
    month_datetime = datetime.strptime(month_date, '%m-%Y')
    month_key = month_datetime.strftime('%m/%Y')
    if month_key not in months_db:
        return {"Message: Item not Found"}
    updated_month = update_months_db(month)
    return updated_month

@app.delete("/singles/{single_id}")
async def delete_single(single_id: int):
    del singles_db[single_id]
    return {"message": "Item deleted successfully"}

@app.delete("/monthly/bankroll{month_date}")
async def delete_bankroll(month_date):
    month_datetime = datetime.strptime(month_date, '%m-%Y')
    month_key = month_datetime.strftime('%m/%Y')
    del months_db[month_key]
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
    current_date = start_date

    for bet in bets_in_date_range:
        sport = bet.sport
        if sport not in betting_summary.sports:
            betting_summary.sports[sport] = Record(wins=0, losses=0, pushes=0, win_percentage=0)
        betting_summary.total_profit += format_decimal(bet.net_profit)
        added_odds += bet.odds
    
    while current_date <= end_date:
        month_key = current_date.strftime('%m/%Y')
        if month_key in months_db:
            month_data = months_db[month_key]
            month_start = max(start_date, date(current_date.year, current_date.month, 1))
            month_end = min(end_date, date(current_date.year, current_date.month, (current_date.replace(day=28) + timedelta(days=4)).day))

            bets_in_month = [
                bet for bet in bets_in_date_range if month_start <= bet.timestamp.date() <= month_end
            ]

            month_profit = sum(format_decimal(bet.profit_number) for bet in bets_in_month)
            month_unit_profit = month_profit / month_data.unit_size
            betting_summary.unit_profit += month_unit_profit
            
        current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    betting_summary.growth = f"{round(betting_summary.total_profit / bets_in_date_range[0].month_bankroll.bankroll * 100)}%"
    betting_summary.total_profit = format_currency(betting_summary.total_profit)
    betting_summary.avg_odds = round(added_odds/len(bets_in_date_range), 2)
    return betting_summary