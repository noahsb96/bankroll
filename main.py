from fastapi import FastAPI
app = FastAPI()
from pydantic import BaseModel, validator
from fastapi.encoders import jsonable_encoder
from typing import Optional
from datetime import datetime, date
import locale
locale.setlocale(locale.LC_ALL, 'C')

class Single(BaseModel):
    result: str
    pick: str 
    sport: str
    units: float
    odds: float
    unit_size: float
    timestamp: Optional[datetime] = None

    @validator('timestamp', pre=True, always=True)
    def parse_date_string(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%m/%d/%Y')
            except ValueError:
                raise ValueError("timestamp must be in the format MM/DD/YYYY")
        return value

class Record(BaseModel):
    wins: int
    losses: int
    pushes: int
    win_percentage: int

class Time(BaseModel):
    month: str
    bankroll: float
    units_size: float
    total_profit: float
    unit_profit: float
    avg_odds: float
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
    nfl: Record
    nba: Record
    mlb: Record
    ncaaf: Record
    ncaab: Record
    nhl: Record
    wnba: Record
    cfl: Record
    boxing: Record
    ufc: Record
    soccer: Record
    other: Record

singles_db = {}
next_id = 0

def format_currency(amount):
    return '${:,.2f}'.format(amount)

def profit(object, item):
    if item.result == "won":
        wager = item.unit_size * item.units
        profit = item.odds * wager
        profit_currency = format_currency(profit)
        object.update({"profit": profit_currency, "wager": wager})
    elif item.result == "lost":
        wager = item.unit_size * item.units
        profit = 0 - wager
        profit_currency = format_currency(profit)
        object.update({"profit": profit_currency, "wager":wager})
    else:
        wager = item.unit_size * item.units
        profit = 0
        profit_currency = format_currency(profit)
        object.update({"profit": profit_currency, "wager":wager})

@app.get("/singles/daily")
async def get_daily_bets():
    today = datetime.now().date()
    daily_bets = [single for single in singles_db.values() if single["timestamp"].date() == today]
    return daily_bets

@app.get("/singles/by_date/{date}")
async def get_bets_by_date(date: date):
    bets_on_date = [single for single in singles_db.values() if single["timestamp"].date() == date]
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
async def create_item(single: Single):
    global next_id
    single.timestamp = single.timestamp or datetime.now()
    single_dict = single.model_dump()
    profit(single_dict, single)
    singles_db[next_id] = single_dict
    next_id += 1
    return single_dict

@app.put("/singles/{single_id}", response_model=Single)
async def update_single(single_id: int, single: Single):
    update_single_encoded = jsonable_encoder(single)
    singles_db[single_id] = update_single_encoded
    profit(update_single_encoded, single)
    return update_single_encoded

@app.delete("/singles/{single_id}")
async def delete_single(single_id: int):
        del singles_db[single_id]
        return {"message": "Item deleted successfully"}
