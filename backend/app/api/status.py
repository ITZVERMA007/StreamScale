from fastapi import APIRouter,HTTPException
from app.core.job_store import get_job
from celery.result import AsyncResult
from app.core.celery_app import celery_app
from worker.tasks.ffmpeg import RESOLUTIONS

router = APIRouter()

# Endpoint to check the status of the desired task with the help of task id which is being generated at the time of file upload
@router.get("/tasks/{task_id}/status")
def get_status(task_id:str):
    job = get_job(task_id)

    if not job:
        raise HTTPException(status_code=404,detail="Task not found")
    
    # This is checking for the status of the task by connecting the backend to the redis
    result  = AsyncResult(task_id,app=celery_app)

    current_state = job.get("status","pending")

    if result.state == "PROGRESS":
        progress_data = result.info if isinstance(result.info,dict) else {}

        # Gets the percent complete for the keys present in the RESOLUTIONS which are the original resolutions
        active_progress_values = [ progress_data.get(res,0) for res in RESOLUTIONS.keys()]

        if active_progress_values:
            overall_progress = sum(active_progress_values)/len(active_progress_values)
        else:
            overall_progress = 0
        return {
            "task_id": task_id,
            "state": "Processing",
            "overall_progress": int(overall_progress),
            "details": progress_data
        }

    elif result.state == "SUCCESS":
        current_state = "Completed"
        current_progress = 100

        downloads = {res: f"/tasks/{task_id}/download/{res}" for res in RESOLUTIONS.keys()}
        return {
            "task_id":task_id,
            "state":current_state,
            "progress":current_progress,
            "download_urls":downloads,
        }
    elif result.state == "FAILURE":
        return {"task_id": task_id, "state": "Failed", "error": str(result.info)}
    
    
