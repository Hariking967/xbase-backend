# XBase Python Backend

Python code execution service for XBase AI platform.

## Features

- ✅ FastAPI REST API
- ✅ Python code execution with timeout
- ✅ Matplotlib visualization support
- ✅ Base64 image encoding
- ✅ CSV data handling
- ✅ Helper utilities for visualizations

## Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Server runs on http://localhost:8000
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Execute Python code
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "result = {\"message\": \"Hello from Python!\"}"
  }'
```

## Deployment to Render

### Option 1: Via Render Dashboard

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `xbase-python-backend`
   - **Root Directory:** `xbase-backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** Free

### Option 2: Via render.yaml

Add this `render.yaml` to your repository root:

```yaml
services:
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

## API Endpoints

### POST /execute

Execute Python code.

**Request:**

```json
{
  "code": "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1,2,3])\nresult = fig",
  "csv": "optional,csv,data",
  "files": {},
  "timeoutMs": 20000
}
```

**Response:**

```json
{
  "prints": "any print output",
  "result": {
    "image_base64": "...",
    "image_mime": "image/png",
    "data": [...],
    "metrics": {...}
  },
  "error": null
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "service": "xbase-python-backend"
}
```

## Environment Variables

- `PORT` - Server port (default: 8000)

## Architecture

```
main.py           - FastAPI server
runner.py         - Python code executor
helpers.py        - Visualization utilities
requirements.txt  - Python dependencies
```

## Security Notes

- Code executes in subprocess with timeout
- Temporary directories auto-cleaned
- No persistent file storage
- Configure CORS for your domain in production

## Usage from Next.js

```typescript
const response = await fetch("http://localhost:8000/execute", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    code: pythonCode,
    csv: csvData,
    timeoutMs: 20000,
  }),
});

const result = await response.json();
```
