from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    singles = relationship("Single", back_populates="owner")

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
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="singles")