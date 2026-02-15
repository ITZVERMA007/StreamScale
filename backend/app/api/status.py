from fastapi import APIRouter,HTTPException
from app.core.job_store import get_job

router = APIRouter()

# Endpoint to check the status of the desired task with the help of task id which is being generated at the time of file upload
@router.get("/tasks/{task_id}/status")
def get_status(task_id:str):
    job = get_job(task_id)

    if not job:
        raise HTTPException(status_code=404,detail="Task not found")
    
    return{
        "task_id":job["task_id"],
        "state":job["status"],
        "progress":job["progress"]
    }
