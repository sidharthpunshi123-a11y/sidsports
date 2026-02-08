import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/sports_betting")
    
    # API Keys (You'll need to sign up for these)
    ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")  # Get from https://the-odds-api.com
    
    # Betting Parameters
    MIN_ODDS = 1.01
    MAX_ODDS = 1.5
    MIN_CONFIDENCE = 0.65  # Minimum predicted probability
    MAX_PARLAY_LEGS = 5
    BANKROLL_PERCENTAGE = 0.02  # 2% of bankroll per bet
    
    # Sports to track
    SPORTS = [
        "soccer_epl",
        "basketball_nba",
        "americanfootball_nfl",
        "cricket_test_match",
        "cricket_odi",
        "basketball_euroleague"
    ]
    
    # Update Schedule
    UPDATE_HOUR = 6  # Update at 6 AM daily
    
    # API Settings
    API_RATE_LIMIT = 500  # Requests per day for free tier
    
config = Config()
