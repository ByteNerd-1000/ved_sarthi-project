"""
Multilingual AI Healthcare Chatbot
Main FastAPI application for healthcare education chatbot
"""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from app.database import init_db, initialize_sample_data
from app.models.alert import AlertService
from app.routers import alerts, chatbot, evaluation, health_data

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic (replaces deprecated @app.on_event)."""
    # --- startup ---
    await init_db()
    try:
        await initialize_sample_data()
    except Exception as e:
        print(f"Note: Sample data initialization: {e}")

    # Start alert monitoring in the background
    async def run_monitoring():
        alert_service = AlertService()
        await alert_service.start_monitoring()

    asyncio.create_task(run_monitoring())

    yield  # application runs here

    # --- shutdown (add cleanup here if needed) ---


app = FastAPI(
    title="Healthcare Chatbot API",
    description="Multilingual AI chatbot for preventive healthcare education",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# Using "*" while RENDER_BACKEND_URL is not yet known.
# After you deploy to Vercel, replace "*" with your exact Vercel URL, e.g.:
#   "https://veda-sarthi.vercel.app"
# NOTE: You cannot mix "*" with specific origins — use one or the other.
ALLOWED_ORIGINS = [
    "*",
    # "https://your-app.vercel.app",   ← uncomment & fill in after deploy
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,          # must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(health_data.router, prefix="/api/health-data", tags=["health-data"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])


# ---------------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/chatbot", response_class=HTMLResponse)
async def serve_chatbot_page():
    """Serve the chatbot HTML page if it exists at the project root."""
    html_path = Path(__file__).parent.parent.parent / "chatbot.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse(
        content="<h1>Chatbot page not found. Make sure chatbot.html exists in the project root.</h1>"
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple homepage with links to the chatbot and API docs."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Healthcare Chatbot</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1   { color: #667eea; }
                .link {
                    display: inline-block; margin: 10px; padding: 10px 20px;
                    background: #667eea; color: white; text-decoration: none; border-radius: 5px;
                }
                .link:hover { background: #764ba2; }
            </style>
        </head>
        <body>
            <h1>🏥 Healthcare Chatbot</h1>
            <p>Welcome to the Healthcare Chatbot API!</p>
            <h2>Quick Links:</h2>
            <a href="/chatbot" class="link">💬 Open Chatbot</a>
            <a href="/docs"    class="link">📚 API Documentation</a>
            <a href="/health"  class="link">❤️ Health Check</a>
            <h2>API Endpoints:</h2>
            <ul>
                <li><strong>POST /api/chatbot/chat</strong>        — Chat with the bot</li>
                <li><strong>GET  /api/alerts/active</strong>        — Get active alerts</li>
                <li><strong>GET  /api/evaluation/accuracy</strong>  — Get accuracy stats</li>
            </ul>
        </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

