# Postman Testing Guide for PatentScope API

## Base URL
```
https://hospitable-generosity-pharmyrus.up.railway.app
```

## API Endpoints

### 1. Health Check

**Request:**
- **Method:** `GET`
- **URL:** `https://hospitable-generosity-pharmyrus.up.railway.app/health`
- **Headers:** None required

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

### 2. API Information

**Request:**
- **Method:** `GET`
- **URL:** `https://hospitable-generosity-pharmyrus.up.railway.app/`
- **Headers:** None required

**Expected Response:**
```json
{
  "message": "PatentScope Scraper API",
  "version": "1.0.0",
  "endpoints": {
    "POST /search": "Execute a patent search",
    "GET /status/{task_id}": "Get search task status",
    "GET /tasks": "List all tasks",
    "GET /health": "Health check"
  }
}
```

---

### 3. Execute Patent Search

**Request:**
- **Method:** `POST`
- **URL:** `https://hospitable-generosity-pharmyrus.up.railway.app/search`
- **Headers:**
  - `Content-Type: application/json`

**Body (JSON):**
```json
{
  "term": "semaglutide",
  "limit": 50,
  "countries": ["US", "EP"],
  "use_login": false,
  "get_details": false
}
```

**Minimal Body (only required field):**
```json
{
  "term": "semaglutide"
}
```

**Full Body (with all options):**
```json
{
  "term": "semaglutide",
  "limit": 100,
  "countries": ["US", "EP", "WO", "CN"],
  "use_login": false,
  "get_details": true,
  "max_details": 20
}
```

**Expected Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Search task created. Use the task_id to check status at /status/{task_id}"
}
```

---

### 4. Check Task Status

**Request:**
- **Method:** `GET`
- **URL:** `https://hospitable-generosity-pharmyrus.up.railway.app/status/{task_id}`
  - Replace `{task_id}` with the actual task ID from step 3
  - Example: `https://hospitable-generosity-pharmyrus.up.railway.app/status/550e8400-e29b-41d4-a716-446655440000`
- **Headers:** None required

**Expected Response (Queued):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "progress": null,
  "result": null,
  "error": null
}
```

**Expected Response (Running):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": "Searching in US...",
  "result": null,
  "error": null
}
```

**Expected Response (Completed):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": "Found 25 unique patents",
  "result": {
    "search_info": {
      "termo": "semaglutide",
      "data_busca": "2024-01-01T12:00:00",
      "total_encontrado": 25,
      "total_unico": 25,
      "paises_filtro": ["US", "EP"],
      "limite": 50,
      "detalhes_completos": false
    },
    "statistics": {
      "por_pais": {
        "US": 15,
        "EP": 10
      },
      "por_ano": {
        "2023": 10,
        "2022": 8,
        "2021": 7
      },
      "top_applicants": {
        "Novo Nordisk": 5,
        "Eli Lilly": 3
      },
      "top_inventors": {}
    },
    "total_patents": 25,
    "patents": [
      {
        "publicationNumber": "US20230123456A1",
        "title": "Semaglutide composition...",
        "publicationDate": "2023-05-15",
        "applicants": ["Novo Nordisk"],
        "inventors": ["John Doe"]
      }
    ]
  },
  "error": null
}
```

---

### 5. List All Tasks

**Request:**
- **Method:** `GET`
- **URL:** `https://hospitable-generosity-pharmyrus.up.railway.app/tasks`
- **Headers:** None required

**Expected Response:**
```json
{
  "total": 5,
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00"
    },
    {
      "task_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "running",
      "created_at": "2024-01-01T12:05:00"
    }
  ]
}
```

---

## Step-by-Step Postman Workflow

### Setup Collection

1. **Open Postman**
2. **Create New Collection:**
   - Click "New" → "Collection"
   - Name it "PatentScope API"

3. **Add Base URL Variable:**
   - In the collection, click "Variables" tab
   - Add variable:
     - Variable: `base_url`
     - Initial Value: `https://hospitable-generosity-pharmyrus.up.railway.app`
     - Current Value: `https://hospitable-generosity-pharmyrus.up.railway.app`

### Test Workflow

**Step 1: Health Check**
1. Create new request in collection
2. Name it "1. Health Check"
3. Method: `GET`
4. URL: `{{base_url}}/health`
5. Click "Send"
6. Should return status 200 with `{"status": "healthy"}`

**Step 2: Execute Search**
1. Create new request
2. Name it "2. Execute Search"
3. Method: `POST`
4. URL: `{{base_url}}/search`
5. Go to "Body" tab → Select "raw" → Select "JSON"
6. Paste this JSON:
```json
{
  "term": "semaglutide",
  "limit": 10,
  "countries": ["US"]
}
```
7. Click "Send"
8. Copy the `task_id` from the response

**Step 3: Check Status**
1. Create new request
2. Name it "3. Check Status"
3. Method: `GET`
4. URL: `{{base_url}}/status/PASTE_TASK_ID_HERE`
5. Click "Send"
6. Keep clicking "Send" every 5 seconds until status is "completed"

**Step 4: View All Tasks**
1. Create new request
2. Name it "4. List Tasks"
3. Method: `GET`
4. URL: `{{base_url}}/tasks`
5. Click "Send"

---

## PowerShell Commands (Windows)

### Simple Test
```powershell
# Health check
Invoke-RestMethod -Uri "https://hospitable-generosity-pharmyrus.up.railway.app/health"

# Start search
$body = @{
    term = "semaglutide"
    limit = 10
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://hospitable-generosity-pharmyrus.up.railway.app/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "Task ID: $($response.task_id)"

# Check status (replace TASK_ID)
Invoke-RestMethod -Uri "https://hospitable-generosity-pharmyrus.up.railway.app/status/TASK_ID"
```

---

## cURL Commands (Linux/Mac/Git Bash)

### Health Check
```bash
curl https://hospitable-generosity-pharmyrus.up.railway.app/health
```

### Execute Search
```bash
curl -X POST https://hospitable-generosity-pharmyrus.up.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "term": "semaglutide",
    "limit": 10,
    "countries": ["US"]
  }'
```

### Check Status
```bash
# Replace TASK_ID with actual task ID
curl https://hospitable-generosity-pharmyrus.up.railway.app/status/TASK_ID
```

### List Tasks
```bash
curl https://hospitable-generosity-pharmyrus.up.railway.app/tasks
```

---

## Interactive API Documentation

The easiest way to test is using the built-in Swagger UI:

**Open in browser:**
```
https://hospitable-generosity-pharmyrus.up.railway.app/docs
```

This provides:
- Interactive interface to test all endpoints
- Automatic request/response documentation
- Try-it-out functionality
- No Postman needed!

**Alternative documentation:**
```
https://hospitable-generosity-pharmyrus.up.railway.app/redoc
```

---

## Sample Search Parameters

### Quick Test (Fast)
```json
{
  "term": "aspirin",
  "limit": 5
}
```

### By Country
```json
{
  "term": "covid vaccine",
  "limit": 20,
  "countries": ["US", "EP"]
}
```

### With Details (Slower)
```json
{
  "term": "semaglutide",
  "limit": 10,
  "get_details": true,
  "max_details": 5
}
```

### Multiple Countries
```json
{
  "term": "artificial intelligence",
  "limit": 50,
  "countries": ["US", "EP", "WO", "CN", "JP"]
}
```

---

## Troubleshooting

### Issue: 404 Not Found
- Check the URL is correct
- Ensure Railway app is deployed and running

### Issue: Timeout
- Search tasks can take 30-60 seconds
- Keep polling `/status/{task_id}` every 5 seconds

### Issue: Task stays in "queued" status
- Check Railway logs in dashboard
- May indicate scraper initialization issue

### Issue: Search returns 0 results
- Try a simpler search term
- Check if PatentScope website is accessible

---

## Expected Response Times

- **Health Check:** < 1 second
- **Start Search:** < 1 second (returns task_id immediately)
- **Search Completion:** 30-90 seconds depending on:
  - Number of patents requested
  - Number of countries
  - Whether `get_details` is enabled

---

## Next Steps

1. Test in Postman using the workflow above
2. Or use the Swagger UI at `/docs` for easier testing
3. Once working, integrate into your application
4. Monitor Railway logs for any issues
