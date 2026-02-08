import os
   import uvicorn

   if __name__ == "__main__":
       port = int(os.environ.get("PORT", 8000))
       uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```
5. **Scroll down**
6. **Click "Commit changes"**

### Step 2: Update Railway Start Command

1. **Go back to Railway**
2. **Click your backend service**
3. **Click "Settings"** tab
4. Find **"Start Command"**
5. **Clear everything** and put:
```
   python start.py
```
6. Railway will auto-redeploy

---

## ⏳ Wait for Deployment

1. **Click "Deployments"** tab
2. Watch the logs
3. You should see:
```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:XXXX
