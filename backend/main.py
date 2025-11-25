"""
API de Agendamento - Clínica de Psicologia UNIPAR Cianorte.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

from backend.database import create_db_and_tables
from backend.seed_data import seed_database
from backend.logger import logger
from backend.routers import auth, rooms, patients, users, appointments
from backend.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando aplicação...")
    create_db_and_tables()
    try:
        seed_database()
    except Exception as e:
        logger.warning(f"Falha ao popular banco na inicializacao: {e}")
    yield
    logger.info("Encerrando aplicação...")


app = FastAPI(lifespan=lifespan)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Primeiro, adicionar CORSMiddleware padrão
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Depois, adicionar um middleware ASGI que garante que o header
# Access-Control-Allow-Origin seja definido EXATAMENTE como a origem
# quando esta estiver na lista ALLOWED_ORIGINS.
class CORSFixerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Responder preflight de forma explícita
        if request.method == "OPTIONS":
            origin = request.headers.get("origin")
            headers = {}
            if origin and origin in ALLOWED_ORIGINS:
                headers = {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS,HEAD",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept",
                    "Access-Control-Allow-Credentials": "true",
                }
            return Response(status_code=200, headers=headers)

        response = await call_next(request)
        origin = request.headers.get("origin")
        if origin and origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

app.add_middleware(CORSFixerMiddleware)

# Registrar routers
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(patients.router)
app.include_router(users.router)
app.include_router(appointments.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Servidor rodando normalmente"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail} [{request.method} {request.url.path}]")
    return JSONResponse(status_code=exc.status_code, content={"success": False, "message": exc.detail, "detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {str(exc)} [{request.method} {request.url.path}]", exc_info=True)
    return JSONResponse(status_code=500, content={"success": False, "message": "Erro interno do servidor."})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG, log_level=settings.LOG_LEVEL.lower())


