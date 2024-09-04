from sqlalchemy.orm import Session
from sqlalchemy import Date, cast
from datetime import datetime, date
from typing import Any
import models, schemas

def profit_calculation(single: Any) -> None:
    unit_size = single.month.unit_size
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
        raise ValueError("Incorrect Result Entered. Enter Win, Loss, Or Push")

def get_daily_bets(db: Session, date: datetime = datetime.now().date()):
    return db.query(models.Single).filter(cast(models.Single.timestamp, Date) == date).all()

def get_bets_by_date(db: Session, date: date):
    return db.query(models.Single).filter(cast(models.Single.timestamp, Date) == date).all()

def get_single(db: Session, single_id: int):
    return db.query(models.Single).filter(models.Single.id == single_id).first()

def get_singles(db: Session, limit: int = 100):
    return db.query(models.Single).limit(limit).all()

def get_bankrolls(db: Session, limit: int = 100):
    return db.query(models.Month).filter(models.Month).limit(limit).all()

def get_bankrolls_by_month(db: Session, month: date):
    return db.query(models.Month).filter(cast(models.Single.month_bankroll, Date) == month)

def create_single(db: Session, single: schemas.SingleCreate, month: schemas.Month):
    single_timestamp = datetime.now() if single_timestamp is None else single_timestamp
    single_profit = profit_calculation(single)
    month_key = single.month_bankroll.strftime('%m/%Y')
    month_exists = db.query(models.Month).filter_by(month_year=month_key).first() is not None
    db_month = models.Month(month_year=month_key, bankroll=month.bankroll, unit_size=month.unit_size)
    db_single=models.Single(result=single.result, pick=single.pick, sport=single.sport, units=single.units, odds=single.odds, timestamp=single_timestamp, profit=single_profit, wager=single.wager, month_bankroll=month_key, net_profit=single_profit-single.wager)
    if month_exists:
        pass
    else:
        db.add(db_month)
    db.add(db_single)