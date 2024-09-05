from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Date, cast
from datetime import datetime, date
from typing import Any
import models, schemas

def profit_calculation(single: schemas.SingleCreate) -> dict:
    unit_size = single.unit_size
    wager = unit_size * single.units
    profit_number = 0
    if single.result == "won":
        profit_number = single.odds * wager
    elif single.result == "lost":
        profit_number = -wager
    elif single.result == "push":
        profit_number = 0
    else:
        raise ValueError("Incorrect Result Entered. Enter Win, Loss, Or Push")
    
    return {
        'wager': wager,
        'profit_number': profit_number
    }

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

def create_single(db: Session, single: schemas.SingleCreate):
    single_timestamp = datetime.now() if single_timestamp is None else single_timestamp
    single_profit = profit_calculation(single)
    wager = single_profit['wager']
    profit_number = single_profit['profit_number']
    month_key = single.month_bankroll.strftime('%m/%Y')
    db_month = db.query(models.Month).filter_by(month_year=single.month_bankroll).first()
    if db_month is None:
        db_month = models.Month(
            month_year=single.month_bankroll,
            bankroll=single.bankroll,
            unit_size=single.unit_size
            )
        db.add(db_month)
    db_single=models.Single(
        result=single.result,
        pick=single.pick,
        sport=single.sport,
        units=single.units,
        odds=single.odds,
        timestamp=single_timestamp,
        profit=profit_number,
        net_profit=profit_number - wager,
        wager=wager,
        month_bankroll=single.month_bankroll
        )
    db_single.month = db_month
    db.add(db_single)
    try:
        db.commit()
        db.refresh(db_single)
        return db_single
    except IntegrityError:
        db.rollback()
        raise