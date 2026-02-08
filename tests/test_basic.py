"""
Basic tests for the sports betting backend
Run with: pytest tests/test_basic.py
"""

import pytest
from app.predictor import BettingPredictor
from app.config import config

def test_config_loaded():
    """Test that configuration is loaded"""
    assert config.MIN_ODDS > 0
    assert config.MAX_ODDS > config.MIN_ODDS
    assert len(config.SPORTS) > 0

def test_predictor_initialization():
    """Test predictor can be initialized"""
    predictor = BettingPredictor()
    assert predictor is not None

def test_implied_probability():
    """Test odds to probability conversion"""
    predictor = BettingPredictor()
    
    # Test 1.5 odds = 66.67% probability
    prob = predictor.calculate_implied_probability(1.5)
    assert abs(prob - 0.6667) < 0.01
    
    # Test 2.0 odds = 50% probability
    prob = predictor.calculate_implied_probability(2.0)
    assert abs(prob - 0.5) < 0.01
    
    # Test 4.0 odds = 25% probability
    prob = predictor.calculate_implied_probability(4.0)
    assert abs(prob - 0.25) < 0.01

def test_expected_value():
    """Test EV calculation"""
    predictor = BettingPredictor()
    
    # Positive EV scenario
    ev = predictor.calculate_value(0.7, 1.5)  # 70% prob, 1.5 odds
    assert ev > 0  # Should have positive EV
    
    # Negative EV scenario
    ev = predictor.calculate_value(0.4, 1.5)  # 40% prob, 1.5 odds
    assert ev < 0  # Should have negative EV

def test_game_analysis():
    """Test game analysis function"""
    predictor = BettingPredictor()
    
    mock_game = {
        'sport': 'basketball_nba',
        'home_team': 'Lakers',
        'away_team': 'Warriors',
        'commence_time': '2024-01-01T19:00:00',
        'home_odds': 1.3,
        'away_odds': 3.5,
        'draw_odds': None
    }
    
    result = predictor.analyze_game(mock_game)
    
    # Should return a dictionary
    assert isinstance(result, dict)
    
    # Should have recommended key
    assert 'recommended' in result

def test_parlay_generation():
    """Test parlay generation"""
    predictor = BettingPredictor()
    
    # Create mock predictions
    predictions = [
        {
            'recommended': True,
            'sport': 'basketball_nba',
            'home_team': 'Lakers',
            'away_team': 'Warriors',
            'outcome': 'home',
            'odds': 1.3,
            'predicted_probability': 0.75,
            'confidence_score': 0.75,
            'commence_time': '2024-01-01'
        },
        {
            'recommended': True,
            'sport': 'soccer_epl',
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'outcome': 'home',
            'odds': 1.4,
            'predicted_probability': 0.72,
            'confidence_score': 0.72,
            'commence_time': '2024-01-01'
        }
    ]
    
    parlays = predictor.generate_parlays(predictions)
    
    # Should generate at least one parlay
    assert len(parlays) > 0
    
    # Check parlay structure
    parlay = parlays[0]
    assert 'legs' in parlay
    assert 'total_odds' in parlay
    assert 'combined_probability' in parlay

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
