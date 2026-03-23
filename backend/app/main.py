from fastapi import FastAPI
from app.api.routes import api_router as v1_router
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Streamscale_API")

origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ok"}

app.include_router(v1_router)