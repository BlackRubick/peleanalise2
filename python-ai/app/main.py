from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import analysis, reports

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.on_event("startup")
async def startup():
    from app.services.ai_model import get_model
    get_model()  # Pre-load model at startup
    print(f"[Startup] {settings.APP_NAME} ready")
