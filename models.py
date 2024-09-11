from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Month(Base):
    __tablename__ = "months"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    month_year = Column(DateTime, unique=True, index=True)
    bankroll = Column(DECIMAL)
    unit_size = Column(DECIMAL)

    singles = relationship("Single", back_populates="month")

class Single(Base):
    __tablename__ = "singles"

    id = Column(Integer, primary_key=True)
    result = Column(String)
    pick = Column(String)
    sport = Column(String)
    units = Column(DECIMAL)
    odds = Column(DECIMAL)
    timestamp = Column(DateTime)
    profit = Column(DECIMAL)
    net_profit = Column(DECIMAL)
    wager = Column(DECIMAL)
    month_id = Column(Integer, ForeignKey('months.id'))

    month = relationship("Month", back_populates="singles")