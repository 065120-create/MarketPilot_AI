"""MarketPilot AI - Main Application"""
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles  
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback

from app.config import settings
from app.api.routes import router as api_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("marketpilot")

@asynccontextmanager  
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting MarketPilot AI v" + settings.APP_VERSION)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Initialize RAG
    try:
        from app.rag.ingest import ingest_knowledge_base
        kb_path = Path(settings.KNOWLEDGE_BASE_DIR)
        if kb_path.exists() and any(kb_path.glob('*.md')):
            stats = ingest_knowledge_base(str(kb_path))
            logger.info(f"📚 RAG initialized: {stats}")
    except Exception as e:
        logger.warning(f"RAG init warning (non-fatal): {e}")
    
    logger.info(f"✅ MarketPilot AI ready at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📊 LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"🔗 n8n: {'Enabled' if settings.N8N_ENABLED else 'Disabled'}")
    yield
    logger.info("👋 MarketPilot AI shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent Marketing Campaign Optimization & Customer Response Automation",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router)

frontend_dir = Path(__file__).parent.parent / "frontend"

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    if (frontend_dir / "css").exists():
        app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
    if (frontend_dir / "js").exists():
        app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "n8n_enabled": settings.N8N_ENABLED
    }

from fastapi import HTTPException

# Page routes - serve all frontend HTML pages both with clean URLs and .html extensions
PAGES = [
    ("index.html", ["/", "/index", "/index.html"]),
    ("dashboard.html", ["/dashboard", "/dashboard.html"]),
    ("campaign.html", ["/campaign", "/campaign.html"]),
    ("upload.html", ["/upload", "/upload.html"]),
    ("agents.html", ["/agents", "/agents.html"]),
    ("insights.html", ["/insights", "/insights.html"]),
    ("segments.html", ["/segments", "/segments.html"]),
    ("journey.html", ["/journey", "/journey.html"]),
    ("optimization.html", ["/optimization", "/optimization.html"]),
    ("budget.html", ["/budget", "/budget.html"]),
    ("scenarios.html", ["/scenarios", "/scenarios.html"]),
    ("recommendations.html", ["/recommendations", "/recommendations.html"]),
    ("rag.html", ["/rag", "/rag.html"]),
    ("reports.html", ["/reports", "/reports.html"]),
]

for html_file, routes in PAGES:
    file_path = frontend_dir / html_file
    if file_path.exists():
        def make_handler(fp):
            async def handler():
                return FileResponse(str(fp), media_type="text/html")
            return handler
        handler_fn = make_handler(file_path)
        for route_path in routes:
            app.add_api_route(route_path, handler_fn, methods=["GET"], response_class=HTMLResponse)

# Dynamic fallback to serve any .html page requested from frontend directory
@app.get("/{page_name}.html", response_class=HTMLResponse)
async def serve_html_page(page_name: str):
    file_path = frontend_dir / f"{page_name}.html"
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path), media_type="text/html")
    raise HTTPException(status_code=404, detail=f"Page {page_name}.html not found")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )
