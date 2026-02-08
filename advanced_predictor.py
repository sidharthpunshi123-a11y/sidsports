"""
Advanced Sports Betting Predictor - Player Props & Team Stats
Focuses on NBA player props and Premier League detailed statistics
Requires 90%+ confidence for recommendations
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedPredictor:
    """
    Advanced prediction engine focusing on:
    - NBA player props (points, assists, rebounds)
    - Premier League team stats (fouls, shots, corners)
    - Historical data analysis
    - 90%+ confidence requirement
    """
    
    def __init__(self):
        self.min_confidence = 0.90  # 90% minimum
        self.min_odds = 1.10
        self.max_odds = 1.50
        self.min_games_sample = 10  # Need at least 10 games of history
        
    def analyze_player_prop(self, player_stats: Dict, prop_line: float, 
                           prop_type: str) -> Dict:
        """
        Analyze a player prop bet based on historical performance
        
        Args:
            player_stats: Historical game stats for player
            prop_line: The betting line (e.g., 20.5 points)
            prop_type: Type of prop (points, assists, rebounds, etc.)
            
        Returns:
            Analysis with confidence, recommendation, reasoning
        """
        if not player_stats or len(player_stats.get('games', [])) < self.min_games_sample:
            return {'recommended': False, 'reason': 'Insufficient historical data'}
        
        games = player_stats['games']
        recent_games = games[-20:]  # Last 20 games
        
        # Calculate key metrics
        values = [g.get(prop_type, 0) for g in recent_games]
        
        avg = np.mean(values)
        std = np.std(values)
        median = np.median(values)
        
        # Count how many times player went OVER the line
        over_count = sum(1 for v in values if v > prop_line)
        hit_rate = over_count / len(values)
        
        # Recent trend (last 5 games weighted more)
        recent_5 = values[-5:]
        recent_avg = np.mean(recent_5)
        recent_over = sum(1 for v in recent_5 if v > prop_line)
        recent_hit_rate = recent_over / 5
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_prop_confidence(
            avg=avg,
            median=median,
            std=std,
            prop_line=prop_line,
            hit_rate=hit_rate,
            recent_hit_rate=recent_hit_rate,
            recent_avg=recent_avg
        )
        
        # Only recommend if confidence >= 90%
        if confidence < self.min_confidence:
            return {
                'recommended': False,
                'confidence': confidence,
                'reason': f'Confidence {confidence:.1%} below 90% threshold'
            }
        
        return {
            'recommended': True,
            'prop_type': prop_type,
            'prop_line': prop_line,
            'player_avg': avg,
            'recent_avg': recent_avg,
            'hit_rate': hit_rate,
            'recent_hit_rate': recent_hit_rate,
            'confidence': confidence,
            'reasoning': self._generate_reasoning(
                player_stats['name'],
                prop_type,
                prop_line,
                avg,
                hit_rate,
                recent_hit_rate
            )
        }
    
    def _calculate_prop_confidence(self, avg: float, median: float, 
                                   std: float, prop_line: float,
                                   hit_rate: float, recent_hit_rate: float,
                                   recent_avg: float) -> float:
        """
        Calculate confidence score for a prop bet
        
        Factors:
        1. How far above line is the average (safety margin)
        2. Historical hit rate
        3. Recent form (weighted higher)
        4. Consistency (low standard deviation = higher confidence)
        """
        
        # 1. Safety margin: How much cushion above the line
        margin = (avg - prop_line) / prop_line
        margin_score = min(margin * 2, 0.30)  # Max 30% contribution
        
        # 2. Historical hit rate (weighted 25%)
        hit_score = hit_rate * 0.25
        
        # 3. Recent form (weighted 30% - most important)
        recent_score = recent_hit_rate * 0.30
        
        # 4. Consistency bonus
        # Lower std deviation = more consistent = higher confidence
        if std > 0:
            consistency = 1 / (1 + (std / avg))
            consistency_score = consistency * 0.15
        else:
            consistency_score = 0.15
        
        total_confidence = margin_score + hit_score + recent_score + consistency_score
        
        # Cap at 0.99 (never claim 100% certainty)
        return min(total_confidence, 0.99)
    
    def _generate_reasoning(self, player_name: str, prop_type: str,
                           prop_line: float, avg: float, hit_rate: float,
                           recent_hit_rate: float) -> str:
        """Generate human-readable reasoning for the recommendation"""
        
        return (
            f"{player_name} averages {avg:.1f} {prop_type} per game. "
            f"Line is {prop_line}, giving a {avg - prop_line:.1f} cushion. "
            f"Hit OVER in {hit_rate:.0%} of games historically, "
            f"and {recent_hit_rate:.0%} in last 5 games."
        )
    
    def analyze_team_stat_prop(self, team_stats: Dict, prop_line: float,
                               stat_type: str) -> Dict:
        """
        Analyze team stat prop bets (fouls, shots, corners, etc.)
        
        Args:
            team_stats: Historical team statistics
            prop_line: The betting line
            stat_type: Type of stat (fouls, shots_on_target, corners, etc.)
        """
        
        if not team_stats or len(team_stats.get('games', [])) < self.min_games_sample:
            return {'recommended': False, 'reason': 'Insufficient data'}
        
        games = team_stats['games']
        recent_games = games[-15:]  # Last 15 games
        
        values = [g.get(stat_type, 0) for g in recent_games]
        
        avg = np.mean(values)
        median = np.median(values)
        std = np.std(values)
        
        over_count = sum(1 for v in values if v > prop_line)
        hit_rate = over_count / len(values)
        
        # Calculate confidence
        margin = (avg - prop_line) / prop_line if prop_line > 0 else 0
        
        # For team stats, we're more conservative
        confidence = (hit_rate * 0.50) + (min(margin * 1.5, 0.30)) + 0.10
        
        if confidence < self.min_confidence:
            return {
                'recommended': False,
                'confidence': confidence,
                'reason': f'Confidence {confidence:.1%} below threshold'
            }
        
        return {
            'recommended': True,
            'stat_type': stat_type,
            'prop_line': prop_line,
            'team_avg': avg,
            'hit_rate': hit_rate,
            'confidence': confidence,
            'reasoning': (
                f"Team averages {avg:.1f} {stat_type} per game. "
                f"Line is {prop_line}. Hit OVER in {hit_rate:.0%} of games."
            )
        }
    
    def generate_prop_parlay(self, all_props: List[Dict], 
                            max_legs: int = 8) -> List[Dict]:
        """
        Generate optimal parlay combinations from individual prop bets
        
        Args:
            all_props: List of all recommended prop bets
            max_legs: Maximum legs per parlay (default 8)
        
        Returns:
            List of parlay recommendations
        """
        
        # Filter for only recommended props
        valid_props = [p for p in all_props if p.get('recommended')]
        
        if len(valid_props) < 2:
            return []
        
        # Sort by confidence
        valid_props.sort(key=lambda x: x['confidence'], reverse=True)
        
        parlays = []
        
        # Create parlays of different sizes
        for size in range(5, min(len(valid_props) + 1, max_legs + 1)):
            # Take top N most confident props
            legs = valid_props[:size]
            
            # Calculate combined confidence
            # Note: This is simplified - actual probability is product
            individual_confidences = [leg['confidence'] for leg in legs]
            combined_confidence = np.prod(individual_confidences)
            
            # Only include if combined confidence still >= 90%
            if combined_confidence < 0.90:
                continue
            
            # Estimate combined odds (simplified)
            # In reality, you'd get actual parlay odds from bookmaker
            estimated_odds = 1.0
            for leg in legs:
                # Assume odds inversely related to probability
                implied_prob = leg['confidence']
                leg_odds = 1 / implied_prob if implied_prob > 0 else 1.5
                # Cap odds to realistic range
                leg_odds = max(self.min_odds, min(leg_odds, self.max_odds))
                estimated_odds *= leg_odds
            
            parlay = {
                'num_legs': size,
                'legs': legs,
                'combined_confidence': combined_confidence,
                'estimated_odds': estimated_odds,
                'expected_value': (combined_confidence * estimated_odds) - 1,
                'reasoning': f"{size}-leg parlay with {combined_confidence:.1%} confidence"
            }
            
            parlays.append(parlay)
        
        # Sort by expected value
        parlays.sort(key=lambda x: x['combined_confidence'], reverse=True)
        
        return parlays[:5]  # Return top 5


class DataFetcher:
    """
    Fetches historical player and team statistics
    
    In production, this would call real APIs like:
    - NBA: stats.nba.com, basketball-reference.com
    - Premier League: fbref.com, understat.com
    """
    
    def get_nba_player_stats(self, player_name: str) -> Dict:
        """
        Fetch NBA player historical stats
        
        In production, integrate with:
        - NBA Stats API
        - Basketball Reference
        - ESPN API
        """
        
        # MOCK DATA - Replace with real API calls
        # This is example data structure
        return {
            'name': player_name,
            'games': [
                {'points': 28, 'assists': 6, 'rebounds': 4},
                {'points': 31, 'assists': 5, 'rebounds': 3},
                {'points': 26, 'assists': 7, 'rebounds': 5},
                {'points': 29, 'assists': 6, 'rebounds': 4},
                {'points': 24, 'assists': 8, 'rebounds': 3},
                {'points': 27, 'assists': 6, 'rebounds': 4},
                {'points': 30, 'assists': 5, 'rebounds': 5},
                {'points': 25, 'assists': 7, 'rebounds': 4},
                {'points': 28, 'assists': 6, 'rebounds': 3},
                {'points': 32, 'assists': 5, 'rebounds': 4},
                {'points': 26, 'assists': 7, 'rebounds': 5},
                {'points': 29, 'assists': 6, 'rebounds': 4},
                {'points': 27, 'assists': 6, 'rebounds': 3},
                {'points': 31, 'assists': 5, 'rebounds': 4},
                {'points': 28, 'assists': 7, 'rebounds': 5},
            ]
        }
    
    def get_epl_team_stats(self, team_name: str) -> Dict:
        """
        Fetch Premier League team stats
        
        In production, integrate with:
        - FBRef.com API
        - Understat
        - Official Premier League API
        """
        
        # MOCK DATA
        return {
            'name': team_name,
            'games': [
                {'fouls': 8, 'shots': 18, 'shots_on_target': 7, 'corners': 6},
                {'fouls': 10, 'shots': 15, 'shots_on_target': 6, 'corners': 8},
                {'fouls': 9, 'shots': 20, 'shots_on_target': 9, 'corners': 7},
                {'fouls': 7, 'shots': 16, 'shots_on_target': 5, 'corners': 5},
                {'fouls': 11, 'shots': 19, 'shots_on_target': 8, 'corners': 9},
                {'fouls': 8, 'shots': 17, 'shots_on_target': 7, 'corners': 6},
                {'fouls': 9, 'shots': 21, 'shots_on_target': 10, 'corners': 8},
                {'fouls': 10, 'shots': 16, 'shots_on_target': 6, 'corners': 7},
                {'fouls': 8, 'shots': 18, 'shots_on_target': 8, 'corners': 6},
                {'fouls': 9, 'shots': 19, 'shots_on_target': 7, 'corners': 7},
                {'fouls': 7, 'shots': 17, 'shots_on_target': 6, 'corners': 5},
                {'fouls': 10, 'shots': 20, 'shots_on_target': 9, 'corners': 8},
            ]
        }


# Example usage
if __name__ == "__main__":
    predictor = AdvancedPredictor()
    fetcher = DataFetcher()
    
    # Analyze NBA player prop
    print("=== NBA Player Prop Analysis ===")
    jalen_stats = fetcher.get_nba_player_stats("Jalen Brunson")
    analysis = predictor.analyze_player_prop(
        player_stats=jalen_stats,
        prop_line=20.5,
        prop_type='points'
    )
    print(f"Recommended: {analysis.get('recommended')}")
    print(f"Confidence: {analysis.get('confidence', 0):.1%}")
    print(f"Reasoning: {analysis.get('reasoning')}")
    
    # Analyze EPL team stat
    print("\n=== Premier League Team Stat ===")
    city_stats = fetcher.get_epl_team_stats("Man City")
    team_analysis = predictor.analyze_team_stat_prop(
        team_stats=city_stats,
        prop_line=5.5,
        stat_type='corners'
    )
    print(f"Recommended: {team_analysis.get('recommended')}")
    print(f"Confidence: {team_analysis.get('confidence', 0):.1%}")
    print(f"Reasoning: {team_analysis.get('reasoning')}")
