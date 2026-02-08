from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import init_db, get_db, Game, Parlay, BankrollTracker
from app.scheduler import scheduler
from app.predictor import BettingPredictor
from app.data_fetcher import DataFetcher
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sports Betting Prediction API",
    description="AI-powered sports betting predictions with parlay recommendations",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class GamePrediction(BaseModel):
    id: int
    sport: str
    home_team: str
    away_team: str
    commence_time: datetime
    predicted_outcome: str
    predicted_probability: float
    confidence_score: float
    home_odds: float
    away_odds: float
    draw_odds: Optional[float] = None
    
    class Config:
        from_attributes = True

class ParlayRecommendation(BaseModel):
    id: int
    parlay_date: datetime
    legs: List[dict]
    total_odds: float
    combined_probability: float
    recommended_stake: float
    result: Optional[str] = None
    
    class Config:
        from_attributes = True

class PerformanceStats(BaseModel):
    total_predictions: int
    correct_predictions: int
    accuracy: float
    total_parlays: int
    winning_parlays: int
    parlay_win_rate: float
    total_roi: float
    average_odds: float

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler"""
    logger.info("Starting application...")
    init_db()
    scheduler.start()
    logger.info("Application started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on shutdown"""
    scheduler.stop()
    logger.info("Application shutdown complete")

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Sports Betting Prediction API",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/predictions/today", response_model=List[GamePrediction])
async def get_todays_predictions(
    sport: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get today's game predictions
    
    Args:
        sport: Optional sport filter (e.g., 'basketball_nba')
    """
    query = db.query(Game).filter(
        Game.commence_time >= datetime.utcnow(),
        Game.commence_time < datetime.utcnow() + timedelta(days=1)
    )
    
    if sport:
        query = query.filter(Game.sport == sport)
    
    predictions = query.order_by(Game.confidence_score.desc()).all()
    
    return predictions

@app.get("/predictions/upcoming", response_model=List[GamePrediction])
async def get_upcoming_predictions(
    days: int = Query(default=7, ge=1, le=30),
    min_confidence: float = Query(default=0.65, ge=0.5, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Get upcoming game predictions
    
    Args:
        days: Number of days to look ahead (1-30)
        min_confidence: Minimum confidence score filter (0.5-1.0)
    """
    end_date = datetime.utcnow() + timedelta(days=days)
    
    predictions = db.query(Game).filter(
        Game.commence_time >= datetime.utcnow(),
        Game.commence_time <= end_date,
        Game.confidence_score >= min_confidence
    ).order_by(Game.commence_time).all()
    
    return predictions

@app.get("/parlays/recommended", response_model=List[ParlayRecommendation])
async def get_recommended_parlays(
    pending_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get recommended parlay bets
    
    Args:
        pending_only: If True, only return unsettled parlays
    """
    query = db.query(Parlay)
    
    if pending_only:
        query = query.filter(Parlay.result == 'pending')
    
    parlays = query.order_by(Parlay.combined_probability.desc()).limit(10).all()
    
    return parlays

@app.get("/parlays/history", response_model=List[ParlayRecommendation])
async def get_parlay_history(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get historical parlay results
    
    Args:
        limit: Number of results to return
    """
    parlays = db.query(Parlay).filter(
        Parlay.result != 'pending'
    ).order_by(Parlay.settled_at.desc()).limit(limit).all()
    
    return parlays

@app.get("/stats/performance", response_model=PerformanceStats)
async def get_performance_stats(db: Session = Depends(get_db)):
    """Get overall system performance statistics"""
    
    # Game predictions stats
    total_games = db.query(Game).filter(Game.settled == True).count()
    correct_games = db.query(Game).filter(
        Game.settled == True,
        Game.predicted_outcome == Game.actual_outcome
    ).count()
    
    # Parlay stats
    total_parlays = db.query(Parlay).filter(Parlay.result != 'pending').count()
    winning_parlays = db.query(Parlay).filter(Parlay.result == 'win').count()
    
    # Calculate ROI
    all_settled_parlays = db.query(Parlay).filter(Parlay.result != 'pending').all()
    total_staked = sum(p.recommended_stake for p in all_settled_parlays)
    total_returned = sum(p.actual_return or 0 for p in all_settled_parlays)
    
    roi = ((total_returned - total_staked) / total_staked * 100) if total_staked > 0 else 0
    
    # Average odds
    avg_odds = db.query(Parlay).filter(
        Parlay.result != 'pending'
    ).with_entities(Parlay.total_odds).all()
    average_odds = sum(o[0] for o in avg_odds) / len(avg_odds) if avg_odds else 0
    
    return PerformanceStats(
        total_predictions=total_games,
        correct_predictions=correct_games,
        accuracy=(correct_games / total_games * 100) if total_games > 0 else 0,
        total_parlays=total_parlays,
        winning_parlays=winning_parlays,
        parlay_win_rate=(winning_parlays / total_parlays * 100) if total_parlays > 0 else 0,
        total_roi=round(roi, 2),
        average_odds=round(average_odds, 2)
    )

@app.post("/trigger/update")
async def trigger_manual_update():
    """
    Manually trigger odds update and prediction generation
    (Useful for testing or forcing refresh)
    """
    try:
        scheduler.daily_update()
        return {"status": "success", "message": "Update triggered successfully"}
    except Exception as e:
        logger.error(f"Manual update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sports/available")
async def get_available_sports():
    """Get list of available sports"""
    from app.config import config
    return {
        "sports": config.SPORTS,
        "count": len(config.SPORTS)
    }

@app.get("/predictions/by-sport/{sport}", response_model=List[GamePrediction])
async def get_predictions_by_sport(
    sport: str,
    db: Session = Depends(get_db)
):
    """Get predictions filtered by specific sport"""
    predictions = db.query(Game).filter(
        Game.sport == sport,
        Game.commence_time >= datetime.utcnow()
    ).order_by(Game.confidence_score.desc()).all()
    
    if not predictions:
        raise HTTPException(status_code=404, detail=f"No predictions found for {sport}")
    
    return predictions

@app.get("/analysis/value-bets", response_model=List[GamePrediction])
async def get_value_bets(
    min_ev: float = Query(default=0.05, ge=0.01, le=0.5),
    db: Session = Depends(get_db)
):
    """
    Get bets with positive expected value
    
    Args:
        min_ev: Minimum expected value threshold
    """
    # In a real implementation, you'd calculate EV and filter
    # For now, return high confidence bets
    predictions = db.query(Game).filter(
        Game.commence_time >= datetime.utcnow(),
        Game.confidence_score >= 0.70
    ).order_by(Game.confidence_score.desc()).limit(20).all()
    
    return predictions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
