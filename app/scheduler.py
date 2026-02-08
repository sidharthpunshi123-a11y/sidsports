from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from app.database import SessionLocal, Game, Parlay
from app.data_fetcher import DataFetcher
from app.predictor import BettingPredictor
from app.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BettingScheduler:
    """
    Automated scheduler for fetching odds, making predictions,
    and updating results
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.data_fetcher = DataFetcher()
        self.predictor = BettingPredictor()
        
    def start(self):
        """Start the scheduler"""
        # Daily update at configured hour
        self.scheduler.add_job(
            self.daily_update,
            CronTrigger(hour=config.UPDATE_HOUR, minute=0),
            id='daily_update',
            name='Daily predictions update',
            replace_existing=True
        )
        
        # Check for settled games every 2 hours
        self.scheduler.add_job(
            self.check_results,
            'interval',
            hours=2,
            id='check_results',
            name='Check game results',
            replace_existing=True
        )
        
        # Run initial update immediately
        self.scheduler.add_job(
            self.daily_update,
            'date',
            run_date=datetime.now(),
            id='initial_update'
        )
        
        self.scheduler.start()
        logger.info("Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def daily_update(self):
        """
        Main daily update job:
        1. Fetch latest odds
        2. Generate predictions
        3. Create recommended parlays
        4. Store in database
        """
        logger.info("Starting daily update...")
        
        try:
            db = SessionLocal()
            
            # Fetch odds for all sports
            all_odds = self.data_fetcher.fetch_all_sports()
            
            predictions = []
            
            # Analyze each game
            for sport, games in all_odds.items():
                for game in games:
                    # Make prediction
                    prediction = self.predictor.analyze_game(game)
                    
                    if prediction.get('recommended'):
                        predictions.append(prediction)
                        
                        # Store in database
                        db_game = Game(
                            sport=game['sport'],
                            home_team=game['home_team'],
                            away_team=game['away_team'],
                            commence_time=game['commence_time'],
                            home_odds=game['home_odds'],
                            away_odds=game['away_odds'],
                            draw_odds=game.get('draw_odds'),
                            predicted_outcome=prediction['outcome'],
                            predicted_probability=prediction['predicted_probability'],
                            confidence_score=prediction['confidence_score']
                        )
                        db.add(db_game)
            
            # Commit games
            db.commit()
            logger.info(f"Stored {len(predictions)} game predictions")
            
            # Generate parlays
            parlays = self.predictor.generate_parlays(predictions)
            
            # Store parlays
            for parlay in parlays:
                db_parlay = Parlay(
                    parlay_date=datetime.utcnow(),
                    legs=[leg for leg in parlay['legs']],
                    total_odds=parlay['total_odds'],
                    combined_probability=parlay['combined_probability'],
                    recommended_stake=parlay['recommended_stake'],
                    result='pending'
                )
                db.add(db_parlay)
            
            db.commit()
            logger.info(f"Generated {len(parlays)} parlay recommendations")
            
            db.close()
            
            logger.info("Daily update completed successfully")
            
        except Exception as e:
            logger.error(f"Error during daily update: {e}", exc_info=True)
    
    def check_results(self):
        """
        Check results for pending games and parlays
        In production, you'd fetch actual scores from an API
        """
        logger.info("Checking game results...")
        
        try:
            db = SessionLocal()
            
            # Get unsettled games that have started
            unsettled_games = db.query(Game).filter(
                Game.settled == False,
                Game.commence_time < datetime.utcnow()
            ).all()
            
            # In production, fetch actual results from API
            # For now, we'll just log them
            logger.info(f"Found {len(unsettled_games)} games to check")
            
            # Placeholder: You would implement actual result fetching here
            # For example:
            # for game in unsettled_games:
            #     actual_result = fetch_game_result(game.id)
            #     game.actual_outcome = actual_result['winner']
            #     game.settled = True
            
            # db.commit()
            
            # Update parlay results based on settled games
            # self._update_parlay_results(db)
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error checking results: {e}", exc_info=True)
    
    def _update_parlay_results(self, db):
        """Update parlay results when all legs are settled"""
        pending_parlays = db.query(Parlay).filter(
            Parlay.result == 'pending'
        ).all()
        
        for parlay in pending_parlays:
            # Check if all legs are settled
            all_settled = True
            all_won = True
            
            for leg_data in parlay.legs:
                # Find the corresponding game
                game = db.query(Game).filter(
                    Game.home_team == leg_data['home_team'],
                    Game.away_team == leg_data['away_team']
                ).first()
                
                if game and game.settled:
                    if game.actual_outcome != game.predicted_outcome:
                        all_won = False
                else:
                    all_settled = False
            
            if all_settled:
                if all_won:
                    parlay.result = 'win'
                    parlay.actual_return = parlay.total_odds * parlay.recommended_stake
                else:
                    parlay.result = 'loss'
                    parlay.actual_return = 0
                
                parlay.settled_at = datetime.utcnow()
        
        db.commit()

# Global scheduler instance
scheduler = BettingScheduler()
