# Free Deployment Guide 🚀

This guide shows you how to deploy your betting backend for **FREE** using various platforms.

## 🎯 Quick Comparison

| Platform | Database | Build Time | Auto-Deploy | Best For |
|----------|----------|------------|-------------|----------|
| Railway | ✅ Included | Fast | ✅ Yes | Easiest setup |
| Render | ✅ Free tier | Medium | ✅ Yes | Good free tier |
| Fly.io | Need separate | Fast | ✅ Yes | Global edge |
| Heroku | Add-on required | Medium | ✅ Yes | Classic choice |

---

## Option 1: Railway.app (⭐ RECOMMENDED)

**Why Railway?**
- Easiest setup (5 minutes)
- Free PostgreSQL included
- Auto-deploys from GitHub
- $5/month free credit

### Steps:

1. **Sign up**: https://railway.app (Use GitHub)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Database**:
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway auto-creates and links it

4. **Set Environment Variables**:
   - Go to your service
   - Click "Variables"
   - Add:
     ```
     ODDS_API_KEY=your_key_here
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     ```

5. **Deploy**:
   - Railway auto-deploys on every git push
   - Get your public URL from "Settings" → "Public Networking"

**Your API**: `https://your-app.railway.app`

---

## Option 2: Render.com

**Free Tier**: 750 hours/month, auto-sleep after inactivity

### Steps:

1. **Sign up**: https://render.com

2. **Create Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repo
   - Choose "main" branch

3. **Configure**:
   ```
   Name: sports-betting-backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add PostgreSQL**:
   - Click "New" → "PostgreSQL"
   - Free tier: 90 days, then $7/month
   - Copy "Internal Database URL"

5. **Environment Variables** (in web service):
   ```
   DATABASE_URL=<paste internal database URL>
   ODDS_API_KEY=your_key_here
   ```

6. **Deploy**: Render auto-builds and deploys

**Your API**: `https://your-app.onrender.com`

**Note**: Free tier sleeps after 15 min inactivity (30s wake time)

---

## Option 3: Fly.io

**Free Tier**: 3 shared VMs + 3GB storage

### Steps:

1. **Install CLI**:
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login**:
   ```bash
   fly auth signup  # or fly auth login
   ```

3. **Launch App**:
   ```bash
   cd sports-betting-backend
   fly launch
   ```

   Answer prompts:
   - App name: (your choice)
   - Region: Choose closest to you
   - PostgreSQL: Yes
   - Upstash Redis: No

4. **Set Secrets**:
   ```bash
   fly secrets set ODDS_API_KEY=your_key_here
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

**Your API**: `https://your-app.fly.dev`

---

## Option 4: Heroku

**Note**: Heroku removed free tier in Nov 2022. Use Eco dyno ($5/month) or choose Railway/Render.

### If you want to use Heroku:

1. **Install CLI**:
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Download from heroku.com/downloads
   ```

2. **Login & Create**:
   ```bash
   heroku login
   heroku create your-betting-backend
   ```

3. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set Config**:
   ```bash
   heroku config:set ODDS_API_KEY=your_key_here
   ```

5. **Create Procfile**:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

**Your API**: `https://your-betting-backend.herokuapp.com`

---

## 🌐 Connecting Frontend (Netlify/Vercel)

Once backend is deployed, connect your frontend:

```javascript
// In your frontend code
const API_URL = 'https://your-app.railway.app'; // Change to your backend URL

async function getPredictions() {
  const response = await fetch(`${API_URL}/predictions/today`);
  const data = await response.json();
  return data;
}

async function getParlays() {
  const response = await fetch(`${API_URL}/parlays/recommended`);
  const data = await response.json();
  return data;
}
```

### Deploy Frontend to Netlify:

1. Create `netlify.toml`:
   ```toml
   [build]
     command = "npm run build"
     publish = "dist"
   
   [[redirects]]
     from = "/api/*"
     to = "https://your-backend.railway.app/:splat"
     status = 200
   ```

2. Push to GitHub and connect in Netlify dashboard

---

## 🔧 Database Options

If you need separate database:

### Free PostgreSQL Providers:

1. **ElephantSQL**: 20MB free
   - https://www.elephantsql.com
   - Get connection string
   - Add to `DATABASE_URL`

2. **Supabase**: 500MB free
   - https://supabase.com
   - Create project → Get connection string
   - Use "connection pooling" URL

3. **Neon**: 10GB free
   - https://neon.tech
   - Modern serverless PostgreSQL
   - Great for hobby projects

---

## ⚡ Performance Tips

### 1. Prevent Sleep (Render/Heroku free tiers)

Create a cron job to ping your API:

```bash
# Use cron-job.org or similar
GET https://your-app.onrender.com/
Every 10 minutes
```

### 2. Enable Caching

Add to your backend (install `redis`):

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="betting-cache")
```

### 3. Use CDN

If serving static files, use Cloudflare (free tier):
- Point your domain to your backend
- Enable caching in Cloudflare dashboard

---

## 🐛 Troubleshooting

### Issue: "Application Error" on deployment

**Solution**:
- Check logs: `railway logs` or in platform dashboard
- Verify environment variables are set
- Ensure `DATABASE_URL` is correct

### Issue: Database connection timeout

**Solution**:
- Use internal/private database URL (not public)
- Check firewall rules
- Verify database is running

### Issue: Out of memory

**Solution**:
- Reduce worker count in production
- Use connection pooling (already configured)
- Upgrade to paid tier if needed

### Issue: API rate limit exceeded

**Solution**:
- Check The Odds API usage
- Reduce update frequency
- Cache predictions longer
- Upgrade API plan if needed

---

## 💰 Cost Estimates

**100% Free Setup**:
- Railway: $5/month credit (enough for small projects)
- Render: 750 hours free
- The Odds API: 500 requests/month free
- Netlify: 100GB bandwidth free

**Minimal Paid ($5-10/month)**:
- Railway Pro: $5/month
- The Odds API Basic: $15/month (1000 requests)
- Total: ~$20/month for robust setup

**Production Ready ($50-100/month)**:
- Railway/Render: $20/month
- PostgreSQL: $15/month
- The Odds API Pro: $50/month
- Redis: Free or $10/month
- Total: ~$100/month

---

## ✅ Checklist

Before deployment:

- [ ] API key obtained from The Odds API
- [ ] `.env` configured with all variables
- [ ] Database migrations completed
- [ ] Tested locally (`uvicorn app.main:app --reload`)
- [ ] Git repository created and pushed
- [ ] Platform account created
- [ ] Environment variables set on platform
- [ ] Database provisioned and connected
- [ ] First deployment successful
- [ ] API accessible at public URL
- [ ] Tested endpoints with Postman/curl
- [ ] Scheduler running (check logs)

---

## 🎉 You're Live!

Your backend is now deployed! Test it:

```bash
# Replace with your URL
curl https://your-app.railway.app/predictions/today

# Test in browser
https://your-app.railway.app/docs
```

Next: Build your frontend and connect it! 🚀
