from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DateTime, Date
from sqlalchemy.orm import relationship
from .database import Base

class Month(Base):
    __tablename__ = "months"

    month_year = Column(DateTime, primary_key=True, unique=True, index=True)
    bankroll = Column(DECIMAL)
    unit_size = Column(DECIMAL)
    singles = relationship("Single", order_by="Single.id", back_populates="month_bankroll")

class Single(Base):
    __tablename__ = "singles"

    id = Column(Integer, primary_key=True)
    result = Column(String)
    pick = Column(String)
    sport = Column(String)
    units = Column(DECIMAL)
    odds = Column(DECIMAL)
    timestamp = Column(DateTime)
    profit_number = Column(DECIMAL)
    net_profit_number = Column(DECIMAL)
    wager = Column(DECIMAL)
    net_profit = Column(DECIMAL)
    profit = Column(String)
    month_bankroll_id = Column(Integer, ForeignKey('months.month_year'))
    month_bankroll = relationship("Month", back_populates="singles")

class Record(Base):
    __tablename__ = "Records"

    id = Column(Integer, primary_key=True)
    sport = Column(String, unique=True)
    wins = Column(Integer)
    losses = Column(Integer)
    pushes = Column(Integer)
    win_percentage = Column(DECIMAL)
    summary_id = Column(Integer, ForeignKey('summaries.id'))
    summary = relationship("BettingSummary", back_populates="sports")
class BettingSummary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    start_date = Column(Date)
    end_date = Column(Date)
    total_profit = Column(DECIMAL)
    unit_profit = Column(DECIMAL)
    avg_odds = Column(DECIMAL)
    growth = Column(DECIMAL)
    win_rate = Column(DECIMAL)
    roi = Column(DECIMAL)
    units_spent = Column(DECIMAL)
    money_spent = Column(DECIMAL)
    units_won = Column(DECIMAL)
    winnings = Column(DECIMAL)
    wins = Column(Integer)
    losses = Column(Integer)
    pushes = Column(Integer)
    sports = relationship("Record", order_by="Record.id", back_populates="summary")

