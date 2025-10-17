# PatentScope Scraper REST API

A FastAPI-based REST API for searching and retrieving patent data from WIPO PatentScope.

## Deployment on Railway

This API is configured to deploy automatically on Railway.

### Environment Variables

No environment variables are required for basic operation, but you can configure:
- `PORT` - Automatically set by Railway
- Add your WIPO credentials if using authenticated access

## API Endpoints

### 1. Root Endpoint
```
GET /
```
Returns API information and available endpoints.

**Response:**
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

### 2. Health Check
```
GET /health
```
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 3. Execute Patent Search
```
POST /search
```

Execute a patent search and return a task ID for tracking.

**Request Body:**
```json
{
  "term": "semaglutide",
  "limit": 50,
  "countries": ["US", "EP", "WO"],
  "use_login": false,
  "get_details": false,
  "max_details": null
}
```

**Parameters:**
- `term` (required): Search term (e.g., "semaglutide")
- `limit` (optional, default: 50): Maximum number of patents (1-1000)
- `countries` (optional): List of country codes (e.g., ["US", "EP", "WO"])
- `use_login` (optional, default: false): Use WIPO authentication
- `get_details` (optional, default: false): Retrieve complete patent details
- `max_details` (optional): Limit number of patents to get details for

**Response:**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "message": "Search task created. Use the task_id to check status at /status/{task_id}"
}
```

### 4. Get Task Status
```
GET /status/{task_id}
```

Get the status and results of a search task.

**Response (Queued):**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "progress": null,
  "result": null,
  "error": null
}
```

**Response (Running):**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "progress": "Searching in US...",
  "result": null,
  "error": null
}
```

**Response (Completed):**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": "Found 25 unique patents",
  "result": {
    "search_info": {
      "termo": "semaglutide",
      "data_busca": "2024-01-01T12:00:00",
      "total_encontrado": 25,
      "total_unico": 25,
      "paises_filtro": ["US"],
      "limite": 50,
      "detalhes_completos": false
    },
    "statistics": {
      "por_pais": {"US": 25},
      "por_ano": {"2023": 10, "2022": 15},
      "top_applicants": {...},
      "top_inventors": {...}
    },
    "total_patents": 25,
    "patents": [...]
  },
  "error": null
}
```

### 5. List All Tasks
```
GET /tasks
```

List all search tasks.

**Response:**
```json
{
  "total": 5,
  "tasks": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00"
    }
  ]
}
```

## Usage Examples

### Using cURL

**1. Start a search:**
```bash
curl -X POST https://your-railway-app.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "term": "semaglutide",
    "limit": 50,
    "countries": ["US", "EP"],
    "get_details": false
  }'
```

**2. Check status:**
```bash
curl https://your-railway-app.railway.app/status/YOUR_TASK_ID
```

### Using Python

```python
import requests
import time

# API base URL
BASE_URL = "https://your-railway-app.railway.app"

# 1. Start search
response = requests.post(f"{BASE_URL}/search", json={
    "term": "semaglutide",
    "limit": 50,
    "countries": ["US", "EP"],
    "get_details": False
})

task_id = response.json()["task_id"]
print(f"Task created: {task_id}")

# 2. Poll for results
while True:
    status_response = requests.get(f"{BASE_URL}/status/{task_id}")
    data = status_response.json()

    print(f"Status: {data['status']}")

    if data["status"] == "completed":
        print(f"Found {data['result']['total_patents']} patents")
        print(data["result"])
        break
    elif data["status"] == "failed":
        print(f"Error: {data['error']}")
        break

    time.sleep(5)
```

### Using JavaScript/Fetch

```javascript
// 1. Start search
const response = await fetch('https://your-railway-app.railway.app/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    term: 'semaglutide',
    limit: 50,
    countries: ['US', 'EP'],
    get_details: false
  })
});

const { task_id } = await response.json();
console.log('Task created:', task_id);

// 2. Poll for results
const checkStatus = async () => {
  const statusResponse = await fetch(`https://your-railway-app.railway.app/status/${task_id}`);
  const data = await statusResponse.json();

  console.log('Status:', data.status);

  if (data.status === 'completed') {
    console.log('Results:', data.result);
    return data.result;
  } else if (data.status === 'failed') {
    console.error('Error:', data.error);
    return null;
  } else {
    setTimeout(checkStatus, 5000);
  }
};

checkStatus();
```

## API Documentation

Once deployed, visit:
- `https://your-railway-app.railway.app/docs` - Interactive Swagger UI
- `https://your-railway-app.railway.app/redoc` - ReDoc documentation

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API locally
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
```

## Notes

- Search tasks run asynchronously in the background
- Task results are stored in memory (will be lost on restart)
- For production, consider using Redis or a database for task storage
- Screenshots and JSON files are saved in the `resultados/` directory
