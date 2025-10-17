# Railway Deployment Guide

## Step-by-Step Deployment

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended for easy integration)

### 2. Deploy from GitHub

#### Option A: Deploy via Railway Dashboard (Recommended)
1. Click **"New Project"** on Railway dashboard
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub account
4. Select the repository: **`Xlonenzo/pharmyrus_patents`**
5. Railway will automatically:
   - Detect Python project
   - Read `Procfile` and `railway.json`
   - Install dependencies from `requirements.txt`
   - Start the web server with uvicorn

#### Option B: Deploy via Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Link to your GitHub repo
railway link

# Deploy
railway up
```

### 3. Configure Environment (Optional)

Railway automatically sets `PORT` variable. If you need WIPO credentials:

1. Go to your project settings
2. Click **"Variables"** tab
3. Add any environment variables (optional for basic usage)

### 4. Wait for Deployment

Railway will:
- Clone your repository
- Install Python dependencies (this may take 3-5 minutes)
- Build the application
- Start the web server
- Assign a public URL

### 5. Get Your App URL

Once deployed:
1. Go to **"Settings"** tab
2. Under **"Domains"**, you'll see your app URL
3. Click **"Generate Domain"** if not already generated
4. Your URL will be like: `https://pharmyrus-patents-production.up.railway.app`

## Testing Your API

### 1. Health Check

First, verify the API is running:

```bash
curl https://your-app-url.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. Check API Info

```bash
curl https://your-app-url.railway.app/
```

Expected response:
```json
{
  "message": "PatentScope Scraper API",
  "version": "1.0.0",
  "endpoints": {...}
}
```

### 3. Test Interactive Documentation

Open in your browser:
- **Swagger UI**: `https://your-app-url.railway.app/docs`
- **ReDoc**: `https://your-app-url.railway.app/redoc`

You can test all endpoints directly from the Swagger UI!

### 4. Execute a Test Search

**Using cURL:**
```bash
curl -X POST https://your-app-url.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "term": "aspirin",
    "limit": 10,
    "countries": ["US"],
    "get_details": false
  }'
```

**Expected response:**
```json
{
  "task_id": "abc123...",
  "status": "queued",
  "message": "Search task created..."
}
```

### 5. Check Search Status

Copy the `task_id` from the previous response:

```bash
curl https://your-app-url.railway.app/status/abc123...
```

**While running:**
```json
{
  "task_id": "abc123...",
  "status": "running",
  "progress": "Searching in US...",
  "result": null
}
```

**When completed:**
```json
{
  "task_id": "abc123...",
  "status": "completed",
  "progress": "Found 10 unique patents",
  "result": {
    "search_info": {...},
    "statistics": {...},
    "total_patents": 10,
    "patents": [...]
  }
}
```

## Complete Testing Script (Python)

Save this as `test_railway_api.py`:

```python
import requests
import time
import json

# Replace with your Railway URL
BASE_URL = "https://your-app-url.railway.app"

def test_api():
    print("=" * 70)
    print("  Testing PatentScope API on Railway")
    print("=" * 70)

    # 1. Health check
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 2. API info
    print("\n2. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # 3. Start search
    print("\n3. Starting patent search...")
    search_data = {
        "term": "aspirin",
        "limit": 5,
        "countries": ["US"],
        "get_details": False
    }

    response = requests.post(f"{BASE_URL}/search", json=search_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Task ID: {result['task_id']}")

    task_id = result['task_id']

    # 4. Poll for results
    print("\n4. Checking search status...")
    max_attempts = 60  # 5 minutes max
    attempt = 0

    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/status/{task_id}")
        data = response.json()

        print(f"   Attempt {attempt + 1}: Status = {data['status']}", end="")
        if data.get('progress'):
            print(f" | Progress: {data['progress']}")
        else:
            print()

        if data["status"] == "completed":
            print("\n✅ Search completed!")
            print(f"   Found {data['result']['total_patents']} patents")
            print(f"\n   Statistics:")
            print(f"   - Countries: {data['result']['statistics']['por_pais']}")
            print(f"   - Years: {data['result']['statistics']['por_ano']}")

            if data['result']['patents']:
                print(f"\n   First patent:")
                patent = data['result']['patents'][0]
                print(f"   - Number: {patent.get('publicationNumber')}")
                print(f"   - Title: {patent.get('title', '')[:70]}...")
                print(f"   - Date: {patent.get('publicationDate')}")

            break
        elif data["status"] == "failed":
            print(f"\n❌ Search failed!")
            print(f"   Error: {data['error']}")
            break

        attempt += 1
        time.sleep(5)

    if attempt >= max_attempts:
        print("\n⚠️ Timeout waiting for results")

    # 5. List all tasks
    print("\n5. Listing all tasks...")
    response = requests.get(f"{BASE_URL}/tasks")
    print(f"   Total tasks: {response.json()['total']}")

    print("\n" + "=" * 70)
    print("  Testing Complete!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
```

**Run it:**
```bash
# Install requests if needed
pip install requests

# Update the BASE_URL in the script, then run:
python test_railway_api.py
```

## Complete Testing Script (Bash)

Save this as `test_railway_api.sh`:

```bash
#!/bin/bash

# Replace with your Railway URL
BASE_URL="https://your-app-url.railway.app"

echo "======================================================================"
echo "  Testing PatentScope API on Railway"
echo "======================================================================"

# 1. Health check
echo -e "\n1. Testing health endpoint..."
curl -s "$BASE_URL/health" | jq '.'

# 2. API info
echo -e "\n2. Testing root endpoint..."
curl -s "$BASE_URL/" | jq '.'

# 3. Start search
echo -e "\n3. Starting patent search..."
RESPONSE=$(curl -s -X POST "$BASE_URL/search" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "aspirin",
    "limit": 5,
    "countries": ["US"],
    "get_details": false
  }')

echo "$RESPONSE" | jq '.'
TASK_ID=$(echo "$RESPONSE" | jq -r '.task_id')
echo "Task ID: $TASK_ID"

# 4. Poll for results
echo -e "\n4. Checking search status..."
for i in {1..60}; do
  STATUS=$(curl -s "$BASE_URL/status/$TASK_ID")
  STATUS_VALUE=$(echo "$STATUS" | jq -r '.status')

  echo "Attempt $i: Status = $STATUS_VALUE"

  if [ "$STATUS_VALUE" == "completed" ]; then
    echo -e "\n✅ Search completed!"
    echo "$STATUS" | jq '.result'
    break
  elif [ "$STATUS_VALUE" == "failed" ]; then
    echo -e "\n❌ Search failed!"
    echo "$STATUS" | jq '.error'
    break
  fi

  sleep 5
done

# 5. List all tasks
echo -e "\n5. Listing all tasks..."
curl -s "$BASE_URL/tasks" | jq '.'

echo -e "\n======================================================================"
echo "  Testing Complete!"
echo "======================================================================"
```

**Run it:**
```bash
chmod +x test_railway_api.sh
./test_railway_api.sh
```

## Monitoring on Railway

### View Logs
1. Go to your Railway project
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. View **"Build Logs"** and **"Deploy Logs"**

### Check Metrics
1. Click **"Metrics"** tab
2. View CPU, Memory, and Network usage

### Restart Service
1. Go to **"Settings"** tab
2. Click **"Restart"** if needed

## Common Issues

### Issue: Build Failed
**Solution:** Check build logs for missing dependencies or syntax errors

### Issue: Application Crashed
**Solution:**
- Check deploy logs
- Verify Selenium/ChromeDriver compatibility
- Railway may need additional packages for headless Chrome

### Issue: Timeout on Searches
**Solution:**
- Start with small limits (5-10 patents)
- Disable `get_details` for faster results
- Check Railway service limits

### Issue: No Domain Generated
**Solution:**
- Go to Settings > Networking
- Click "Generate Domain"

## Next Steps

Once deployed and tested:
1. ✅ Note your Railway URL
2. ✅ Test with the Swagger UI at `/docs`
3. ✅ Run the test scripts above
4. ✅ Monitor logs for any errors
5. ✅ Scale up if needed (Railway settings)

Your API is now live and ready to use! 🚀
