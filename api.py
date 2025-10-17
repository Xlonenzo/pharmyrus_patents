#!/usr/bin/env python3
"""
FastAPI REST API for PatentScope Scraper
Provides endpoints to execute patent searches
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uuid

from patentscope_scraper import PatentScopeScraper
from patentscope_detalhes import enriquecer_patentes_com_detalhes, agrupar_por_publication_number

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="PatentScope Scraper API",
    description="REST API to search and retrieve patent data from WIPO PatentScope",
    version="1.0.0"
)

# In-memory task storage (use Redis or database in production)
tasks = {}


class SearchRequest(BaseModel):
    """Request model for patent search"""
    term: str = Field(..., description="Search term (e.g., 'semaglutide')")
    limit: int = Field(50, description="Maximum number of patents to retrieve", ge=1, le=1000)
    countries: Optional[List[str]] = Field(None, description="List of country codes to filter (e.g., ['US', 'EP', 'WO'])")
    use_login: bool = Field(False, description="Use WIPO login for authenticated access")
    get_details: bool = Field(False, description="Retrieve complete details for each patent")
    max_details: Optional[int] = Field(None, description="Maximum number of patents to get details for")


class SearchResponse(BaseModel):
    """Response model for search request"""
    task_id: str
    status: str
    message: str


class TaskStatus(BaseModel):
    """Task status response"""
    task_id: str
    status: str
    progress: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None


def execute_search(task_id: str, request: SearchRequest):
    """Background task to execute patent search"""
    try:
        logger.info(f"Starting search task {task_id} with term: {request.term}")
        tasks[task_id]["status"] = "running"
        tasks[task_id]["progress"] = "Initializing scraper..."

        # Initialize scraper
        scraper = PatentScopeScraper(
            headless=True,
            use_demo_mode=False,
            use_login=request.use_login
        )

        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pasta_resultados = Path("resultados") / f"patentscope_{request.term}_{timestamp}"
        pasta_resultados.mkdir(parents=True, exist_ok=True)

        tasks[task_id]["progress"] = f"Searching patents for term: {request.term}"

        # Execute search
        all_patents = []

        if request.countries:
            # Search by country
            for pais in request.countries:
                logger.info(f"Searching in {pais}...")
                tasks[task_id]["progress"] = f"Searching in {pais}..."

                patents = scraper.buscar_patentes(
                    termo_busca=request.term,
                    campo='all',
                    pais=pais,
                    limite=request.limit
                )

                for p in patents:
                    p['pais_filtro'] = pais

                all_patents.extend(patents)
                logger.info(f"Found {len(patents)} patents in {pais}")
        else:
            # General search
            logger.info("Executing general search...")
            tasks[task_id]["progress"] = "Executing general search..."
            all_patents = scraper.buscar_patentes_simples(request.term, limite=request.limit)

        # Remove duplicates
        unique_patents = {}
        for p in all_patents:
            pub_num = p.get('publicationNumber', '')
            if pub_num and pub_num not in unique_patents:
                unique_patents[pub_num] = p

        patents_list = list(unique_patents.values())

        logger.info(f"Found {len(all_patents)} total, {len(patents_list)} unique patents")
        tasks[task_id]["progress"] = f"Found {len(patents_list)} unique patents"

        if len(patents_list) == 0:
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = {
                "message": "No patents found",
                "total_found": 0,
                "patents": []
            }
            return

        # Get complete details if requested
        if request.get_details and len(patents_list) > 0:
            tasks[task_id]["progress"] = f"Retrieving complete details..."
            logger.info(f"Retrieving complete details for patents...")

            try:
                patents_list = enriquecer_patentes_com_detalhes(
                    patents_list,
                    scraper.driver,
                    max_detalhes=request.max_details
                )
                logger.info("Complete details retrieved successfully")
            except Exception as e:
                logger.error(f"Error retrieving details: {e}")
                tasks[task_id]["progress"] = f"Error retrieving details: {str(e)}"

        # Calculate statistics
        stats = {
            "por_pais": {},
            "por_ano": {},
            "top_applicants": {},
            "top_inventors": {}
        }

        # Statistics by country
        for p in patents_list:
            pub_num = p.get('publicationNumber', '')
            if pub_num and len(pub_num) >= 2:
                country = pub_num[:2]
                stats["por_pais"][country] = stats["por_pais"].get(country, 0) + 1

        # Statistics by year
        for p in patents_list:
            date = p.get('publicationDate', '')
            if date and len(date) >= 4:
                year = date[:4]
                stats["por_ano"][year] = stats["por_ano"].get(year, 0) + 1

        # Top applicants
        for p in patents_list:
            for app in p.get('applicants', []):
                if app:
                    stats["top_applicants"][app] = stats["top_applicants"].get(app, 0) + 1

        # Top inventors
        for p in patents_list:
            for inv in p.get('inventors', []):
                if inv:
                    stats["top_inventors"][inv] = stats["top_inventors"].get(inv, 0) + 1

        # Save results
        tasks[task_id]["progress"] = "Saving results..."

        # Grouped patents by publication number
        patents_agrupadas = agrupar_por_publication_number(patents_list)

        json_file = pasta_resultados / "patents_complete.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents_agrupadas, f, ensure_ascii=False, indent=2)

        # Summary with stats
        summary = {
            "search_info": {
                "termo": request.term,
                "data_busca": datetime.now().isoformat(),
                "total_encontrado": len(all_patents),
                "total_unico": len(patents_list),
                "paises_filtro": request.countries,
                "limite": request.limit,
                "detalhes_completos": request.get_details
            },
            "statistics": stats,
            "patents": patents_list
        }

        summary_file = pasta_resultados / "summary_with_stats.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"Search task {task_id} completed successfully")
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = {
            "search_info": summary["search_info"],
            "statistics": summary["statistics"],
            "total_patents": len(patents_list),
            "patents": patents_list[:10],  # Return first 10 patents in response
            "files": {
                "json_complete": str(json_file),
                "summary": str(summary_file)
            }
        }

    except Exception as e:
        logger.error(f"Error in search task {task_id}: {e}", exc_info=True)
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PatentScope Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "POST /search": "Execute a patent search",
            "GET /status/{task_id}": "Get search task status",
            "GET /tasks": "List all tasks",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/search", response_model=SearchResponse)
async def search_patents(request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Execute a patent search

    Returns a task_id that can be used to check the search status
    """
    task_id = str(uuid.uuid4())

    tasks[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "request": request.dict(),
        "created_at": datetime.now().isoformat()
    }

    background_tasks.add_task(execute_search, task_id, request)

    logger.info(f"Created search task {task_id}")

    return SearchResponse(
        task_id=task_id,
        status="queued",
        message="Search task created. Use the task_id to check status at /status/{task_id}"
    )


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a search task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]

    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress"),
        result=task.get("result"),
        error=task.get("error")
    )


@app.get("/tasks")
async def list_tasks():
    """List all search tasks"""
    return {
        "total": len(tasks),
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "created_at": task["created_at"]
            }
            for task_id, task in tasks.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
