from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import estatisticas, operadoras

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (permite Vue.js acessar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(operadoras.router)
app.include_router(estatisticas.router)


@app.get("/")
async def root():
    return {
        "message": "API ANS Operadoras está funcionando!",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    from .database import execute_one

    try:
        result = execute_one("SELECT 1 as test", ())
        db_status = "connected" if result else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {"status": "healthy", "database": db_status}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
