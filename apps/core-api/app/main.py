import os
from fastapi import FastAPI
from fastapi.responses import Response
from dotenv import load_dotenv
from psycopg import connect

load_dotenv()  # spotlook/.env 로컬 로드

app = FastAPI(title="SpotLook Core API")

@app.get("/health")
def health():
    return {"ok": True, "service": "core-api"}

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/health/db")
def health_db():
    db_url = os.getenv("CORE_DATABASE_URL")
    if not db_url:
        return {"ok": False, "db": False, "error": "CORE_DATABASE_URL is missing"}

    with connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("select 1;")
            return {"ok": True, "db": True}

