# 🎯 Sports Betting Backend - QUICK START

## ✅ What's Been Built

A complete, production-ready sports betting prediction backend with:

### Core Features:
- ✅ Multi-sport odds fetching (NFL, NBA, NHL, MLB, EPL, Cricket, etc.)
- ✅ AI prediction algorithm (low odds focus: 1.01-1.5)
- ✅ Automated parlay generation
- ✅ Daily automated updates (configurable schedule)
- ✅ Performance tracking & ROI calculation
- ✅ REST API with 10+ endpoints
- ✅ PostgreSQL database with 4 tables
- ✅ Scheduler for auto-updates every day + results checking every 2 hours

### Files Created:
```
sports-betting-backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration & settings
│   ├── database.py          # Database models (SQLAlchemy)
│   ├── data_fetcher.py      # Odds API integration
│   ├── predictor.py         # Prediction algorithm
│   ├── scheduler.py         # Automated updates
│   └── main.py              # FastAPI application (API endpoints)
├── tests/
│   ├── __init__.py
│   └── test_basic.py        # Unit tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker containerization
├── docker-compose.yml      # Local dev with PostgreSQL
├── Procfile                # Heroku deployment
├── start.sh                # Linux/Mac startup script
├── start.bat               # Windows startup script
├── README.md               # Full documentation
├── DEPLOYMENT.md           # Deployment guide
└── example-frontend.html   # Demo frontend
```

---

## 🚀 How to Get Started (5 Minutes)

### Option 1: Quick Test (No Setup)

1. **Download the backend folder**
2. **Run this command:**
   ```bash
   cd sports-betting-backend
   chmod +x start.sh
   ./start.sh
   ```
3. **The system will auto-generate MOCK data for testing**
4. **Visit:** http://localhost:8000/docs

### Option 2: Full Setup (With Real Data)

1. **Get API Key** (2 minutes):
   - Visit: https://the-odds-api.com
   - Sign up (free)
   - Copy your API key

2. **Setup**:
   ```bash
   cd sports-betting-backend
   
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your API key
   nano .env  # or use any text editor
   ```

3. **Install PostgreSQL** (if not installed):
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   createdb sports_betting
   
   # Or use Docker
   docker-compose up -d db
   ```

4. **Run**:
   ```bash
   ./start.sh
   # Then:
   python -m uvicorn app.main:app --reload
   ```

5. **Open:** http://localhost:8000/docs

---

## 📊 How the Update System Works

### Automatic Updates:

**Daily at 6 AM** (configurable in `app/config.py`):
1. Fetches latest odds from The Odds API
2. Analyzes all upcoming games across configured sports
3. Generates predictions for games with odds between 1.01-1.5
4. Creates optimized 2-5 leg parlays
5. Stores everything in PostgreSQL database

**Every 2 Hours**:
1. Checks for games that have finished
2. Updates results in database
3. Calculates actual ROI
4. Updates parlay win/loss status

### Manual Trigger:
```bash
# Via API
curl -X POST http://localhost:8000/trigger/update

# Or in the browser
http://localhost:8000/docs → Try out POST /trigger/update
```

### View Update Logs:
```bash
# The system logs all updates
# Check console output or deployment platform logs
```

---

## 🌐 Deploying to Free Hosting (Recommended: Railway)

### Railway (5 min setup):

1. **Sign up**: https://railway.app (use GitHub)

2. **New Project** → "Deploy from GitHub repo"

3. **Add PostgreSQL**:
   - Click "+ New" → "Database" → "PostgreSQL"
   - Auto-connects to your app

4. **Set Environment Variables**:
   ```
   ODDS_API_KEY=your_key_here
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```

5. **Done!** Railway auto-deploys
   - Your API: `https://your-app.railway.app`
   - Updates run automatically

### Alternative: Render, Fly.io, Heroku
See `DEPLOYMENT.md` for detailed guides

---

## 📱 Frontend Integration

### Simple Example:

Open `example-frontend.html` in browser and point it to your backend:

```javascript
// Change API URL in the browser
http://localhost:8000  // Local
https://your-app.railway.app  // Deployed
```

### For Netlify/Vercel:

```javascript
const API_URL = 'https://your-backend.railway.app';

// Get today's predictions
fetch(`${API_URL}/predictions/today`)
  .then(r => r.json())
  .then(data => console.log(data));

// Get parlays
fetch(`${API_URL}/parlays/recommended`)
  .then(r => r.json())
  .then(parlays => console.log(parlays));
```

---

## 🔑 Key API Endpoints

| Endpoint | What It Does |
|----------|--------------|
| `GET /predictions/today` | Today's game predictions |
| `GET /predictions/upcoming` | Next 1-30 days predictions |
| `GET /parlays/recommended` | Current parlay recommendations |
| `GET /parlays/history` | Past parlay results |
| `GET /stats/performance` | Win rate, ROI, accuracy |
| `POST /trigger/update` | Force refresh data |
| `GET /sports/available` | List of tracked sports |

### Example Calls:

```bash
# Get today's picks
curl http://localhost:8000/predictions/today

# Get high-confidence bets (75%+)
curl "http://localhost:8000/predictions/upcoming?min_confidence=0.75"

# Get performance stats
curl http://localhost:8000/stats/performance

# Force update
curl -X POST http://localhost:8000/trigger/update
```

---

## ⚙️ Customization

Edit `app/config.py`:

```python
# Change odds range
MIN_ODDS = 1.01  # Lower bound
MAX_ODDS = 1.5   # Upper bound

# Change confidence threshold
MIN_CONFIDENCE = 0.65  # Minimum 65% confident

# Change max parlay size
MAX_PARLAY_LEGS = 5  # Max 5-leg parlays

# Change update time
UPDATE_HOUR = 6  # Run at 6 AM daily

# Add/remove sports
SPORTS = [
    "soccer_epl",      # English Premier League
    "basketball_nba",  # NBA
    "americanfootball_nfl",  # NFL
    # Add more from the-odds-api.com/sports
]
```

---

## 🐛 Troubleshooting

### "No predictions found"
→ Run manual update: `POST /trigger/update`
→ Check if API key is set in `.env`
→ Verify sports have upcoming games

### "Database connection error"
→ Check PostgreSQL is running: `pg_isready`
→ Verify `DATABASE_URL` in `.env`
→ Create database: `createdb sports_betting`

### "API key error"
→ Check key at https://the-odds-api.com/account
→ Free tier = 500 requests/month
→ System uses mock data if no key

### "Scheduler not running"
→ Check logs for errors
→ Manually trigger: `POST /trigger/update`
→ Verify timezone settings

---

## 📊 Understanding the Data

### Prediction Confidence:
- **70-80%**: Good confidence, reasonable odds
- **80-90%**: High confidence, but watch for low odds
- **90%+**: Very high confidence, likely very low odds

### Expected Value (EV):
- **Positive EV**: Good bet (predicted prob > implied prob)
- **Negative EV**: Bad bet (avoid)
- **0 EV**: Break-even bet

### Parlay Recommendations:
- System combines 2-5 high-confidence picks
- Looks for positive expected value
- Recommends 2% bankroll stake
- Shows combined probability

---

## ⚠️ Important Reminders

1. **This is educational** - Sports betting is gambling
2. **No guarantees** - Even 80% win rate has losing streaks
3. **Variance is real** - Expect ups and downs
4. **Bankroll management** - Never bet more than 2-3% per bet
5. **Bookmakers ban winners** - Successful bettors get limited
6. **Legal check** - Ensure betting is legal in your area

---

## 📈 Next Steps

1. ✅ **Test locally** with mock data
2. ✅ **Get API key** for real odds
3. ✅ **Deploy to Railway** (or another platform)
4. ✅ **Build frontend** (use example-frontend.html as template)
5. ✅ **Track performance** over time
6. ✅ **Refine algorithm** based on results

---

## 💡 Pro Tips

- Start with **mock data** to understand the system
- Use **free tier** hosting (Railway/Render) initially
- **Track results** for at least 100 bets before judging
- **Don't chase losses** - stick to the system
- **Combine with manual research** for best results
- **Upgrade API tier** if you need more frequent updates

---

## 🎉 You're Ready!

Your backend is complete and production-ready. The scheduler will automatically:
- Fetch odds daily
- Generate predictions
- Create parlays
- Track performance

Just deploy it and connect your frontend!

**Questions? Check:**
- `README.md` - Full documentation
- `DEPLOYMENT.md` - Deployment guides
- `/docs` endpoint - Interactive API docs

---

**Built with**: Python, FastAPI, PostgreSQL, scikit-learn
**License**: MIT (Educational use)
**Author**: AI-Powered Betting Research
