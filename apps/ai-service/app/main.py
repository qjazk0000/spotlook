from fastapi import FastAPI

app = FastAPI(title="SpotLook AI Service")

@app.get("/health")
def health():
    return {"ok": True, "service": "ai-service"}
