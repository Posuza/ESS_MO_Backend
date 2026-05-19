from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import (
    address,
    department,
    district,
    division,
    employee,
    field,
    name_prefix,
    position,
    position_change_log,
    postal_code,
    province,
    route,
    route_report,
    sub_district,
)
from app.api.endpoints.auth import auth, forgot_password
from app.core.config import settings
from app.core.database import init_db
from app.core.db_error_handler import DatabaseErrorMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create SQLite DB + tables on startup.
    init_db()
    yield


app = FastAPI(
    title="GUTSESS Backend API",
    description="""
    GUTSESS Backend APIs

    ## api Levels

    | no | Name                | list | get1 | update | delete |
    |----|---------------------|------|------|--------|--------|
    | 1  | route               | true | true | true   | true   |
    | 2  | position            | true | true | true   | true   |
    | 3  | position_change_log | true | true | true   | true   |
    | 4  | name_prefix         | true | true | true   | true   |
    | 5  | address             | true | true | true   | true   |
    | 6  | province            | true | true | true   | true   |
    | 7  | district            | true | true | true   | true   |
    | 8  | sub_district        | true | true | true   | true   |
    | 9  | postal_code         | true | true | true   | true   |
    | 10 | department          | true | true | true   | true   |
    | 11 | division            | true | true | true   | true   |
    | 12 | employee            | true | true | true   | true   |
    | 13 | field               | true | true | true   | true   |
    | 14 | route_report        | true | true | true   | true   |


    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Error Handler (catches all DB errors globally)
app.add_middleware(DatabaseErrorMiddleware)


# Custom HTTPException handler to support detail as object
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Include routers
# Auth endpoints (under /api/v1 prefix - matches production)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(forgot_password.router, prefix="/api/v1")

# Other endpoints (with /api/v1 prefix)
app.include_router(route_report.router, prefix="/api/v1")
app.include_router(employee.router, prefix="/api/v1")
app.include_router(field.router, prefix="/api/v1")
app.include_router(department.router, prefix="/api/v1")
app.include_router(division.router, prefix="/api/v1")
app.include_router(route.router, prefix="/api/v1")
app.include_router(position.router, prefix="/api/v1")
app.include_router(position_change_log.router, prefix="/api/v1")
app.include_router(name_prefix.router, prefix="/api/v1")
app.include_router(address.router, prefix="/api/v1")
app.include_router(province.router, prefix="/api/v1")
app.include_router(district.router, prefix="/api/v1")
app.include_router(sub_district.router, prefix="/api/v1")
app.include_router(postal_code.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "PBAC Backend API",
        "version": "1.0.0",
        "architecture": "Brain/Nervous/Hands",
    }


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}
