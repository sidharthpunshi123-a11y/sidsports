import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import logging
from datetime import datetime
from app.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BettingPredictor:
    """
    Advanced prediction engine for sports betting
    Uses ensemble methods and statistical analysis
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.historical_data = {}
        
    def calculate_implied_probability(self, odds: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1 / odds if odds > 0 else 0
    
    def calculate_value(self, predicted_prob: float, odds: float) -> float:
        """
        Calculate expected value of a bet
        Positive EV means good bet
        """
        implied_prob = self.calculate_implied_probability(odds)
        return predicted_prob - implied_prob
    
    def analyze_game(self, game: Dict) -> Dict:
        """
        Analyze a single game and provide prediction
        
        Returns:
            Dictionary with prediction, confidence, and recommended action
        """
        home_prob = self.calculate_implied_probability(game['home_odds'])
        away_prob = self.calculate_implied_probability(game['away_odds'])
        draw_prob = self.calculate_implied_probability(game.get('draw_odds', 0)) if game.get('draw_odds') else 0
        
        # Normalize probabilities (bookmaker's margin removal)
        total_prob = home_prob + away_prob + draw_prob
        if total_prob > 0:
            home_prob = home_prob / total_prob
            away_prob = away_prob / total_prob
            draw_prob = draw_prob / total_prob if draw_prob > 0 else 0
        
        # Enhanced prediction using multiple factors
        features = self._extract_features(game)
        adjusted_home_prob = self._adjust_probability(home_prob, features, 'home')
        adjusted_away_prob = self._adjust_probability(away_prob, features, 'away')
        
        # Determine best outcome
        predictions = {
            'home': (adjusted_home_prob, game['home_odds']),
            'away': (adjusted_away_prob, game['away_odds'])
        }
        
        if draw_prob > 0:
            predictions['draw'] = (draw_prob, game.get('draw_odds', 0))
        
        # Find outcome with highest probability AND acceptable odds
        best_outcome = None
        best_confidence = 0
        best_odds = 0
        
        for outcome, (prob, odds) in predictions.items():
            if config.MIN_ODDS <= odds <= config.MAX_ODDS and prob >= config.MIN_CONFIDENCE:
                if prob > best_confidence:
                    best_outcome = outcome
                    best_confidence = prob
                    best_odds = odds
        
        if not best_outcome:
            return {
                'recommended': False,
                'reason': 'No outcome meets criteria (odds or confidence too low)'
            }
        
        # Calculate expected value
        ev = self.calculate_value(best_confidence, best_odds)
        
        return {
            'recommended': True,
            'outcome': best_outcome,
            'predicted_probability': best_confidence,
            'odds': best_odds,
            'expected_value': ev,
            'confidence_score': best_confidence,
            'sport': game['sport'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'commence_time': game['commence_time']
        }
    
    def _extract_features(self, game: Dict) -> Dict:
        """
        Extract features for prediction
        In production, you'd fetch historical data here
        """
        # Placeholder for feature engineering
        # In real system, fetch:
        # - Head-to-head record
        # - Recent form (last 5-10 games)
        # - Home/away splits
        # - Injuries
        # - Rest days
        # - League position
        
        return {
            'home_advantage': 0.05,  # Typical home advantage
            'form_differential': 0,
            'h2h_advantage': 0,
            'rest_advantage': 0
        }
    
    def _adjust_probability(self, base_prob: float, features: Dict, side: str) -> float:
        """
        Adjust probability based on additional features
        This is simplified - real version would use trained model
        """
        adjustment = 0
        
        if side == 'home':
            adjustment += features['home_advantage']
            adjustment += features['form_differential']
        else:
            adjustment -= features['home_advantage']
            adjustment -= features['form_differential']
        
        adjusted = base_prob + adjustment
        
        # Keep within valid range
        return max(0.01, min(0.99, adjusted))
    
    def generate_parlays(self, predictions: List[Dict]) -> List[Dict]:
        """
        Generate optimal parlay combinations from individual predictions
        
        Args:
            predictions: List of recommended single bets
            
        Returns:
            List of parlay combinations with combined odds and probabilities
        """
        # Filter for recommended bets only
        valid_bets = [p for p in predictions if p.get('recommended', False)]
        
        if len(valid_bets) < 2:
            logger.info("Not enough valid bets for parlays")
            return []
        
        # Sort by confidence
        valid_bets.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        parlays = []
        
        # Create parlays of different sizes
        for parlay_size in range(2, min(len(valid_bets) + 1, config.MAX_PARLAY_LEGS + 1)):
            # Take top N most confident bets
            legs = valid_bets[:parlay_size]
            
            # Calculate combined odds and probability
            combined_odds = 1.0
            combined_probability = 1.0
            
            for leg in legs:
                combined_odds *= leg['odds']
                combined_probability *= leg['predicted_probability']
            
            # Only include if combined probability is still reasonable
            if combined_probability >= 0.4 and combined_odds <= 10.0:
                parlay = {
                    'legs': [
                        {
                            'sport': leg['sport'],
                            'home_team': leg['home_team'],
                            'away_team': leg['away_team'],
                            'outcome': leg['outcome'],
                            'odds': leg['odds'],
                            'probability': leg['predicted_probability']
                        }
                        for leg in legs
                    ],
                    'total_odds': round(combined_odds, 2),
                    'combined_probability': round(combined_probability, 3),
                    'num_legs': parlay_size,
                    'expected_value': round((combined_probability * combined_odds) - 1, 3),
                    'recommended_stake': round(config.BANKROLL_PERCENTAGE * 100, 2)  # Percentage
                }
                
                parlays.append(parlay)
        
        # Sort by expected value
        parlays.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return parlays[:5]  # Return top 5 parlays
    
    def backtest_predictions(self, historical_predictions: List[Dict], 
                            actual_results: List[Dict]) -> Dict:
        """
        Evaluate prediction accuracy against actual results
        
        Returns:
            Performance metrics
        """
        if not historical_predictions or not actual_results:
            return {'error': 'No data for backtesting'}
        
        correct = 0
        total = len(historical_predictions)
        total_roi = 0
        
        for pred, result in zip(historical_predictions, actual_results):
            if pred['outcome'] == result['actual_outcome']:
                correct += 1
                # Calculate return
                stake = 1.0  # Unit stake
                returns = stake * pred['odds']
                profit = returns - stake
                total_roi += profit
            else:
                total_roi -= 1.0  # Lost stake
        
        accuracy = (correct / total) * 100 if total > 0 else 0
        avg_roi = (total_roi / total) * 100 if total > 0 else 0
        
        return {
            'accuracy': round(accuracy, 2),
            'roi': round(avg_roi, 2),
            'total_bets': total,
            'wins': correct,
            'losses': total - correct,
            'win_rate': round(accuracy, 2)
        }
