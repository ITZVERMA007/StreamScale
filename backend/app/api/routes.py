from fastapi import APIRouter
from .upload import router as upload_router
from .status import router as status_router
from .download import router as download_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(upload_router)
api_router.include_router(status_router)
api_router.include_router(download_router)