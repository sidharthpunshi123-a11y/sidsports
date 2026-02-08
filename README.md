# Sports Betting Prediction Backend 🎯

An AI-powered sports betting prediction system that analyzes odds across multiple sports, generates high-confidence predictions, and recommends parlay bets with automated daily updates.

## ⚠️ IMPORTANT DISCLAIMERS

**This system is for EDUCATIONAL and RESEARCH purposes only.**

- Sports betting involves significant financial risk
- Past performance does not guarantee future results
- No prediction system can guarantee profits
- Always bet responsibly and within your means
- This is a learning project, not financial advice

## 🚀 Features

- **Multi-Sport Coverage**: NFL, NBA, NHL, MLB, EPL, Cricket, and more
- **Automated Daily Updates**: Fetches odds and generates predictions automatically
- **Smart Parlay Generator**: Creates optimized multi-leg parlays with calculated probabilities
- **Performance Tracking**: Historical performance metrics and ROI tracking
- **REST API**: Easy integration with any frontend (web, mobile, etc.)
- **Low-Odds Focus**: Targets 1.01-1.5 odds for higher probability outcomes

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 12+
- The Odds API key (free tier available)

## 🛠️ Installation

### 1. Clone and Setup

```bash
cd sports-betting-backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

Install PostgreSQL and create a database:

```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql
createdb sports_betting

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb sports_betting

# Windows: Download from postgresql.org
```

### 3. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
DATABASE_URL=postgresql://yourusername:yourpassword@localhost:5432/sports_betting
ODDS_API_KEY=your_api_key_here
```

**Get your FREE API key:**
1. Visit https://the-odds-api.com
2. Sign up for free account (500 requests/month)
3. Copy your API key to `.env`

### 4. Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

## 🏃 Running the Backend

### Local Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Production

```bash
# Run with Gunicorn (production ASGI server)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/predictions/today` | GET | Today's predictions |
| `/predictions/upcoming` | GET | Upcoming predictions (1-30 days) |
| `/parlays/recommended` | GET | Recommended parlay bets |
| `/parlays/history` | GET | Historical parlay results |
| `/stats/performance` | GET | System performance metrics |
| `/trigger/update` | POST | Manual odds update |

### Example API Calls

```bash
# Get today's predictions
curl http://localhost:8000/predictions/today

# Get recommended parlays
curl http://localhost:8000/parlays/recommended

# Get performance stats
curl http://localhost:8000/stats/performance

# Filter by sport
curl http://localhost:8000/predictions/by-sport/basketball_nba

# Get high-confidence bets
curl "http://localhost:8000/predictions/upcoming?min_confidence=0.75"
```

## ⏰ How Updates Work

The backend automatically updates:

1. **Daily at 6 AM** (configurable in `app/config.py`):
   - Fetches latest odds from The Odds API
   - Analyzes all upcoming games
   - Generates predictions and parlays
   - Stores in database

2. **Every 2 Hours**:
   - Checks for settled games
   - Updates results
   - Calculates ROI

You can also trigger manual updates via API:

```bash
curl -X POST http://localhost:8000/trigger/update
```

## 🌐 Deployment Options

### Option 1: Railway (Easiest - Free Tier Available)

1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Connect your repository
4. Add environment variables in Railway dashboard
5. Railway auto-deploys on git push

**Railway Config:**
- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 2: Render (Free Tier)

1. Sign up at https://render.com
2. Create new "Web Service"
3. Connect GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Create PostgreSQL database (free tier)

### Option 3: Heroku

```bash
# Install Heroku CLI
# Create new app
heroku create your-betting-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set ODDS_API_KEY=your_key_here

# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku main
```

### Option 4: DigitalOcean/AWS/GCP

Use Docker for easy deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t betting-backend .
docker run -p 8000:8000 --env-file .env betting-backend
```

## 🔧 Configuration

Edit `app/config.py` to customize:

```python
# Betting parameters
MIN_ODDS = 1.01          # Minimum odds to consider
MAX_ODDS = 1.5           # Maximum odds (lower = safer)
MIN_CONFIDENCE = 0.65    # Minimum prediction confidence
MAX_PARLAY_LEGS = 5      # Max legs per parlay

# Sports to track
SPORTS = [
    "soccer_epl",
    "basketball_nba",
    # Add more...
]

# Update schedule
UPDATE_HOUR = 6  # Daily update time (24-hour format)
```

## 📈 Frontend Integration

Your frontend (Netlify, Vercel, etc.) can call these endpoints:

```javascript
// Example: Fetch today's predictions
const response = await fetch('https://your-backend.railway.app/predictions/today');
const predictions = await response.json();

// Example: Get recommended parlays
const parlays = await fetch('https://your-backend.railway.app/parlays/recommended');
const data = await parlays.json();
```

## 🧪 Testing Without API Key

The system includes **mock data mode** for testing without an API key:

```python
# In .env, leave ODDS_API_KEY empty or remove it
# System will generate realistic mock data for testing
```

This is perfect for:
- Testing your frontend
- Understanding the system
- Development without API costs

## 📊 Database Schema

The system uses 4 main tables:

1. **games**: Individual game predictions
2. **parlays**: Multi-leg parlay recommendations
3. **historical_performance**: Past game results
4. **bankroll_tracker**: ROI and performance tracking

## 🔍 Monitoring & Logging

Logs are output to console. In production, use a log aggregator:

```bash
# View logs on Railway
railway logs

# View logs on Heroku
heroku logs --tail
```

## ⚡ Performance Optimization

For high traffic:

1. **Add Redis caching**:
```bash
pip install redis
# Cache predictions for 5 minutes
```

2. **Use connection pooling**:
```python
# Already configured in database.py
```

3. **Scale workers**:
```bash
# Run multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🐛 Troubleshooting

**Database connection error:**
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U yourusername -d sports_betting
```

**Scheduler not running:**
- Check logs for errors
- Verify timezone settings
- Manually trigger update: `POST /trigger/update`

**API key errors:**
- Verify key in `.env`
- Check usage at the-odds-api.com/account
- Free tier: 500 requests/month

## 🚨 Important Notes

1. **API Rate Limits**: Free tier = 500 requests/month. Be strategic with updates.

2. **Bankroll Management**: System recommends 2% stakes. NEVER bet more than you can afford to lose.

3. **Variance**: Even 80% win rate has losing streaks. Expect variance.

4. **Bookmaker Limits**: Successful bettors often get limited/banned. This is normal.

5. **Legal**: Ensure sports betting is legal in your jurisdiction.

## 📚 Next Steps

1. **Build Frontend**: Use React, Vue, or plain HTML
2. **Add More Features**: 
   - Email alerts for high-value bets
   - Telegram bot integration
   - Live score tracking
   - Advanced ML models
3. **Improve Predictions**:
   - Add historical data
   - Train custom models
   - Include injury reports
   - Weather data for outdoor sports

## 📄 License

MIT License - Use for educational purposes

## 🤝 Contributing

This is an educational project. Feel free to:
- Report issues
- Suggest improvements
- Add new sports/features

## ⚖️ Final Warning

**Sports betting is gambling. The house always has an edge. Treat this as a learning project in data science and software engineering, not a get-rich-quick scheme.**

Most professional bettors lose money. This system cannot change fundamental market dynamics. Use responsibly or not at all.

---

**Built with**: FastAPI, PostgreSQL, scikit-learn, APScheduler

**Need help?** Check the `/docs` endpoint for interactive API documentation.
