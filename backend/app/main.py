import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import projects, files, agent, ws, memory
from app.services.project_service import project_service
from app.database import init_db, engine
from sqlalchemy import text


# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("summit.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Ensure default demo calculator workspace exists
    logger.info("Initializing Summit AI Coding Workspace backend...")
    init_db()
    demo_id = project_service.ensure_default_demo_project()
    logger.info(f"Default demo project ensured: {demo_id}")
    yield
    # Shutdown
    logger.info("Shutting down Summit backend...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development mode: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(projects.router)
app.include_router(files.router)
app.include_router(agent.router)
app.include_router(ws.router)
app.include_router(memory.router)



@app.get("/api/health")
def health_check():
    """Service health check endpoint with database connectivity check."""
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        db_status = f"error: {e}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model": settings.SUMMIT_MODEL
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
