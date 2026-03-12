import os
from fastapi import FastAPI, Depends
from fastapi.responses import Response

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import engine

from app.api.posts import router as posts_router
from app.api.hotspots import router as hotspots_router

from dotenv import load_dotenv

load_dotenv()  # spotlook/.env 로컬 로드

app = FastAPI(title="SpotLook Core API")

# register routers
app.include_router(posts_router)
app.include_router(hotspots_router)


@app.get("/health")
def health():
    return {"ok": True, "service": "core-api"}

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"ok": True, "db": "connected"}