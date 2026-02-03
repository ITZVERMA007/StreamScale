from fastapi import APIRouter,UploadFile,File

router = APIRouter()

@router.post("/upload")
async def upload_file(file:UploadFile=File(...)):
    return {
        "message":"file received",
        "filename":file.filename
    }
@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    return {
        "task_id": task_id,
        "status": "processing"
    }

@router.get("/tasks/{task_id}/results")
async def get_task_results(task_id: str):
    return {
        "task_id": task_id,
        "results": "dummy results"
    }

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    return {
        "task_id": task_id,
        "status": "cancelled"
    }