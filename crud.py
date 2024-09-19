from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Date, cast
from datetime import datetime, date
from typing import Any
import models, schemas
from decimal import Decimal

def profit_calculation(single: schemas.SingleCreate, unit_size: Decimal) -> dict:
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

def get_or_create_month(db: Session, month_create: schemas.MonthCreate) -> models.Month:
    db_month = db.query(models.Month).filter(models.Month.month_year == month_create.month_year).first()
    if db_month:
        return db_month
    else:
        db_month = models.Month(
            month_year=month_create.month_year,
            bankroll=month_create.bankroll,
            unit_size=month_create.unit_size
        )
        db.add(db_month)
        db.commit()
        db.refresh(db_month)
        return db_month

def create_single(db: Session, single: schemas.SingleCreate) -> models.Single:
    if single.month_year is None:
        single.month_year = single.timestamp.strftime("%m/%Y")
    month_year_str = single.month_year
    db_month = db.query(models.Month).filter(models.Month.month_year == month_year_str).first()
    if not db_month:
        raise ValueError(f"Month {month_year_str} does not exist. Please post the month's bankroll info first.")
    profit_data = profit_calculation(single, db_month.unit_size)
    wager = profit_data['wager']
    profit_number = profit_data['profit_number']
    db_single = models.Single(
        result=single.result,
        pick=single.pick,
        sport=single.sport,
        units=single.units,
        odds=single.odds,
        timestamp=single.timestamp,
        month_year=month_year_str,
        profit=profit_number,
        net_profit=profit_number - wager,
        wager=wager
    )
    db.add(db_single)
    try:
        db.commit()
        db.refresh(db_single)
        return db_single
    except IntegrityError:
        db.rollback()
        raise
