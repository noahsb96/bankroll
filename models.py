from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DateTime, Date
from sqlalchemy.orm import relationship
from .database import Base

class Month(Base):
    __tablename__ = "months"

    month_year = Column(DateTime, primary_key=True, unique=True, index=True)
    bankroll = Column(DECIMAL)
    unit_size = Column(DECIMAL)

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
    
    month_bankroll = relationship("Month", back_populates="months", unique=True, index=True)