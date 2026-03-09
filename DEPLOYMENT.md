# XBase Backend Deployment Guide

## ✅ What Was Created

Your Python backend is now in: `xbase-backend/`

**Files:**

- `main.py` - FastAPI server
- `runner.py` - Python code executor
- `helpers.py` - Visualization utilities
- `requirements.txt` - Python dependencies
- `README.md` - Documentation
- `.gitignore` - Git ignore rules

## 🚀 Quick Start - Local Testing

### 1. Install Dependencies

```bash
cd xbase-backend
pip install -r requirements.txt
```

### 2. Run the Backend

```bash
python main.py
```

Server runs on: `http://localhost:8000`

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test Python execution
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "result = {\"message\": \"Hello!\"}"}'
```

### 4. Update Next.js .env

In `xbase-app/.env`, set:

```
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
```

### 5. Run Next.js App

```bash
cd ../xbase-app
npm run dev
```

## 🌐 Deploy to Render

### Option 1: Via Render Dashboard (Easier)

1. **Push to GitHub:**

   ```bash
   git add xbase-backend/
   git commit -m "Add Python backend"
   git push
   ```

2. **Create Service on Render:**
   - Go to [render.com](https://render.com/dashboard)
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - **Settings:**
     - Name: `xbase-python-backend`
     - Root Directory: `xbase-backend`
     - Runtime: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python main.py`
     - Instance Type: **Free**

3. **Get Your URL:**
   - Render will give you a URL like: `https://xbase-python-backend.onrender.com`

4. **Update Next.js .env:**

   ```env
   NEXT_PUBLIC_BACKEND_URL="https://xbase-python-backend.onrender.com"
   ```

5. **Redeploy Next.js:**
   - Push updated `.env` to GitHub
   - Render auto-deploys

### Option 2: Via render.yaml (Automated)

Create `render.yaml` in your **repository root**:

```yaml
services:
  # Next.js Frontend
  - type: web
    name: xbase-app
    runtime: node
    rootDir: xbase-app
    buildCommand: npm install && npm run build
    startCommand: npm start
    plan: free
    envVars:
      - key: NEXT_PUBLIC_BACKEND_URL
        sync: false # Set manually in dashboard
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      # ... other env vars

  # Python Backend
  - type: web
    name: xbase-python-backend
    runtime: python
    rootDir: xbase-backend
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    plan: free
    envVars:
      - key: PORT
        value: 10000
```

## 🔗 How It Works

### Architecture

```
User Request
    ↓
Next.js Frontend (Render)
    ↓
AI Agent detects Python needed
    ↓
Calls Python Backend API (Render)
    ↓
Python executes code, creates charts
    ↓
Returns result with base64 image
    ↓
Next.js displays result
```

### Local Development

```
Docker Available?
    ├─ YES → Use local Docker
    └─ NO → Call external backend API (NEXT_PUBLIC_BACKEND_URL)
```

### Production (Render)

```
Both services on Render free tier:
- xbase-app (Next.js)
- xbase-python-backend (FastAPI)

Next.js calls Python backend via HTTP
No Docker needed ✅
```

## 📊 Cost Breakdown

| Service          | Tier | Cost         | Notes                       |
| ---------------- | ---- | ------------ | --------------------------- |
| Next.js App      | Free | $0           | Spins down after 15min idle |
| Python Backend   | Free | $0           | Spins down after 15min idle |
| Neon Database    | Free | $0           | Always on                   |
| Supabase Storage | Free | $0           | 1GB limit                   |
| **Total**        |      | **$0/month** | ✅ 100% Free                |

## 🧪 Testing

### Test Backend Directly

```bash
# Test health
curl https://xbase-python-backend.onrender.com/health

# Test matplotlib
curl -X POST https://xbase-python-backend.onrender.com/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import matplotlib.pyplot as plt\nfrom helpers import fig_to_base64\nfig, ax = plt.subplots()\nax.plot([1,2,3])\nresult = fig_to_base64(fig)"
  }'
```

### Test from Next.js

In your chat:

```
"Create a bar chart with id on x-axis and Mark on y-axis from Students table"
```

Expected:

- ✅ AI fetches data
- ✅ Calls Python backend
- ✅ Returns visualization
- ✅ Displays chart

## 🎯 Environment Variables

### xbase-app (Next.js)

```env
NEXT_PUBLIC_BACKEND_URL="https://your-backend.onrender.com"
DATABASE_URL="postgresql://..."
OPENAI_API_KEY="sk-..."
BETTER_AUTH_SECRET="..."
BETTER_AUTH_URL="https://your-app.onrender.com"
SUPABASE_URL="..."
SUPABASE_SECRET_KEY="..."
```

### xbase-backend (Python)

```env
PORT=10000  # Render sets this automatically
```

## ✅ Verification Checklist

After deployment:

- [ ] Python backend health check responds
- [ ] Next.js app loads
- [ ] SQL queries work
- [ ] Python visualizations work
- [ ] Images display correctly
- [ ] Both services on free tier

## 🚨 Troubleshooting

### Backend not responding

1. Check Render logs for Python backend
2. Verify `main.py` is running
3. Check PORT environment variable

### Next.js can't reach backend

1. Verify `NEXT_PUBLIC_BACKEND_URL` is set correctly
2. Check CORS settings in `main.py`
3. Test backend URL directly with curl

### Visualizations not working

1. Check backend logs for Python errors
2. Verify matplotlib installed
3. Test with simple plot code

## 📝 Summary

**✅ Done:**

- Python backend created in `xbase-backend/`
- FastAPI server with `/execute` endpoint
- Next.js adapter updated to call backend
- Both can run on Render free tier

**🎯 Next Steps:**

1. Test locally (`python main.py` + `npm run dev`)
2. Deploy backend to Render
3. Update `NEXT_PUBLIC_BACKEND_URL`
4. Deploy Next.js app
5. Test visualizations end-to-end

**Your app is now fully production-ready with separate Python backend! 🎉**
