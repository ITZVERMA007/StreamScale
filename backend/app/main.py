from fastapi import FastAPI
from app.api.routes import router as v1_router

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok"}

app.include_router(v1_router,prefix="/api/v1")