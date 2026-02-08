from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import config

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True)
    sport = Column(String(50))
    home_team = Column(String(100))
    away_team = Column(String(100))
    commence_time = Column(DateTime)
    home_odds = Column(Float)
    away_odds = Column(Float)
    draw_odds = Column(Float, nullable=True)
    predicted_outcome = Column(String(20))
    predicted_probability = Column(Float)
    confidence_score = Column(Float)
    actual_outcome = Column(String(20), nullable=True)
    settled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Parlay(Base):
    __tablename__ = "parlays"
    
    id = Column(Integer, primary_key=True)
    parlay_date = Column(DateTime)
    legs = Column(JSON)  # Array of game IDs
    total_odds = Column(Float)
    combined_probability = Column(Float)
    recommended_stake = Column(Float)
    result = Column(String(20), nullable=True)  # 'win', 'loss', 'pending'
    actual_return = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)

class HistoricalPerformance(Base):
    __tablename__ = "historical_performance"
    
    id = Column(Integer, primary_key=True)
    sport = Column(String(50))
    home_team = Column(String(100))
    away_team = Column(String(100))
    game_date = Column(DateTime)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    outcome = Column(String(20))
    features = Column(JSON)  # Store calculated features
    created_at = Column(DateTime, default=datetime.utcnow)

class BankrollTracker(Base):
    __tablename__ = "bankroll_tracker"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    starting_balance = Column(Float)
    ending_balance = Column(Float)
    total_staked = Column(Float)
    total_returned = Column(Float)
    num_bets = Column(Integer)
    num_wins = Column(Integer)
    roi = Column(Float)

# Database setup
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
