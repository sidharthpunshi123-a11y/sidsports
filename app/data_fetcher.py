import requests
from datetime import datetime, timedelta
from typing import List, Dict
from app.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch odds and game data from The Odds API"""
    
    def __init__(self):
        self.api_key = config.ODDS_API_KEY
        self.base_url = "https://api.the-odds-api.com/v4"
        
    def get_odds(self, sport: str) -> List[Dict]:
        """
        Fetch current odds for a specific sport
        
        Args:
            sport: Sport key (e.g., 'soccer_epl', 'basketball_nba')
            
        Returns:
            List of games with odds data
        """
        if not self.api_key:
            logger.warning("No API key configured. Using mock data.")
            return self._get_mock_data(sport)
        
        url = f"{self.base_url}/sports/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us,uk,eu",
            "markets": "h2h",  # Head to head (winner)
            "oddsFormat": "decimal",
            "dateFormat": "iso"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data)} games for {sport}")
            
            # Check remaining API quota
            remaining = response.headers.get('x-requests-remaining')
            if remaining:
                logger.info(f"API requests remaining: {remaining}")
            
            return self._parse_odds_data(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching odds for {sport}: {e}")
            return []
    
    def _parse_odds_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Parse raw API response into standardized format"""
        parsed_games = []
        
        for game in raw_data:
            try:
                # Get best odds from available bookmakers
                bookmakers = game.get('bookmakers', [])
                if not bookmakers:
                    continue
                
                # Find best odds for each outcome
                best_odds = self._get_best_odds(bookmakers)
                
                parsed_game = {
                    'id': game.get('id'),
                    'sport': game.get('sport_key'),
                    'commence_time': datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00')),
                    'home_team': game.get('home_team'),
                    'away_team': game.get('away_team'),
                    'home_odds': best_odds.get('home'),
                    'away_odds': best_odds.get('away'),
                    'draw_odds': best_odds.get('draw')
                }
                
                parsed_games.append(parsed_game)
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing game data: {e}")
                continue
        
        return parsed_games
    
    def _get_best_odds(self, bookmakers: List[Dict]) -> Dict[str, float]:
        """Extract best available odds from multiple bookmakers"""
        best_odds = {'home': 0, 'away': 0, 'draw': None}
        
        for bookmaker in bookmakers:
            markets = bookmaker.get('markets', [])
            for market in markets:
                if market['key'] == 'h2h':
                    outcomes = market.get('outcomes', [])
                    for outcome in outcomes:
                        name = outcome['name']
                        odds = outcome['price']
                        
                        # Store highest odds for each outcome
                        if 'home' in outcome or outcomes.index(outcome) == 0:
                            best_odds['home'] = max(best_odds['home'], odds)
                        elif 'away' in outcome or outcomes.index(outcome) == 1:
                            best_odds['away'] = max(best_odds['away'], odds)
                        elif 'draw' in name.lower():
                            if best_odds['draw'] is None:
                                best_odds['draw'] = odds
                            else:
                                best_odds['draw'] = max(best_odds['draw'], odds)
        
        return best_odds
    
    def _get_mock_data(self, sport: str) -> List[Dict]:
        """Generate mock data for testing without API key"""
        logger.info(f"Generating mock data for {sport}")
        
        teams = {
            'soccer_epl': [
                ('Manchester City', 'Arsenal'),
                ('Liverpool', 'Chelsea'),
                ('Tottenham', 'Newcastle')
            ],
            'basketball_nba': [
                ('Lakers', 'Warriors'),
                ('Celtics', 'Heat'),
                ('Bucks', 'Nuggets')
            ],
            'americanfootball_nfl': [
                ('Chiefs', 'Bills'),
                ('49ers', 'Cowboys'),
                ('Eagles', 'Ravens')
            ]
        }
        
        mock_games = []
        game_teams = teams.get(sport, [('Team A', 'Team B')])
        
        for i, (home, away) in enumerate(game_teams):
            mock_games.append({
                'id': f'mock_{sport}_{i}',
                'sport': sport,
                'commence_time': datetime.utcnow() + timedelta(hours=24 + i*6),
                'home_team': home,
                'away_team': away,
                'home_odds': 1.2 + (i * 0.1),
                'away_odds': 4.5 - (i * 0.2),
                'draw_odds': 3.5 if 'soccer' in sport else None
            })
        
        return mock_games
    
    def fetch_all_sports(self) -> Dict[str, List[Dict]]:
        """Fetch odds for all configured sports"""
        all_data = {}
        
        for sport in config.SPORTS:
            odds_data = self.get_odds(sport)
            all_data[sport] = odds_data
        
        return all_data
