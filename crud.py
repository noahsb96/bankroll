from sqlalchemy.orm import Session
from sqlalchemy import Date, cast
from datetime import datetime, date
from . import models, schemas

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
    return db.query(models.Month).filter(cast(models.Month.month_year, Date) == month)
