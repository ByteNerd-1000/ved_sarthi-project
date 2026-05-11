"""
Multilingual AI Healthcare Chatbot
Main FastAPI application for healthcare education chatbot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from pathlib import Path
from dotenv import load_dotenv

from app.routers import chatbot, alerts, health_data, evaluation
from app.database import init_db, initialize_sample_data
from app.models.alert import AlertService

load_dotenv()

app = FastAPI(
    title="Healthcare Chatbot API",
    description="Multilingual AI chatbot for preventive healthcare education",
    version="1.0.0"
)

# CORS middleware
# Add your Vercel frontend URL to this list after deploying
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8002",
    # TODO: Replace with your actual Vercel URL after first deploy, e.g.:
    # "https://veda-sarthi.vercel.app",
    "*",   # Keep "*" for now; restrict after you know your Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    await init_db()
    # Initialize sample data if needed
    try:
        await initialize_sample_data()
    except Exception as e:
        print(f"Note: Sample data initialization: {e}")
    # Start alert monitoring service (run in background)
    import asyncio
    async def run_monitoring():
        alert_service = AlertService()
        await alert_service.start_monitoring()
    asyncio.create_task(run_monitoring())

# Include routers
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(health_data.router, prefix="/api/health-data", tags=["health-data"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Serve the chatbot HTML page (optional; points to project root chatbot.html if present)
@app.get("/chatbot", response_class=HTMLResponse)
async def serve_chatbot_page():
    """Serve the chatbot HTML page"""
    html_path = Path(__file__).parent.parent.parent / "chatbot.html"
    if html_path.exists():
        return FileResponse(html_path)
    else:
        return HTMLResponse(content="<h1>Chatbot page not found. Make sure chatbot.html exists in the project root.</h1>")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve homepage with links to chatbot and API docs"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Healthcare Chatbot</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #667eea; }
                .link { display: inline-block; margin: 10px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
                .link:hover { background: #764ba2; }
            </style>
        </head>
        <body>
            <h1>🏥 Healthcare Chatbot</h1>
            <p>Welcome to the Healthcare Chatbot API!</p>
            <h2>Quick Links:</h2>
            <a href="/chatbot" class="link">💬 Open Chatbot</a>
            <a href="/docs" class="link">📚 API Documentation</a>
            <a href="/health" class="link">❤️ Health Check</a>
            <h2>API Endpoints:</h2>
            <ul>
                <li><strong>POST /api/chatbot/chat</strong> - Chat with the bot</li>
                <li><strong>GET /api/alerts/active</strong> - Get active alerts</li>
                <li><strong>GET /api/evaluation/accuracy</strong> - Get accuracy stats</li>
            </ul>
        </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    # Use a dedicated port (8002) for this project to avoid conflicts
    uvicorn.run(app, host="0.0.0.0", port=8002)

