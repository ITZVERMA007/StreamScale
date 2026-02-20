from fastapi import APIRouter,HTTPException
from app.core.job_store import get_job
from celery.result import AsyncResult
from app.core.celery_app import celery_app
from worker.tasks.ffmpeg import RESOLUTIONS
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Endpoint to check the status of the desired task with the help of task id which is being generated at the time of file upload
@router.get("/tasks/{task_id}/status")
def get_status(task_id:str):
    job = get_job(task_id)

    if not job:
        raise HTTPException(status_code=404,detail="Task not found")
    
    current_state = job.get("status","pending")

    try:
        # This is checking for the status of the task by connecting the backend to the redis
        result  = AsyncResult(task_id,app=celery_app)

        if result.state == "PROGRESS":
            progress_data = result.info if isinstance(result.info,dict) else {}
            tasks = progress_data.get("tasks",{})

            # Gets the percent complete for the keys present in the RESOLUTIONS which are the original resolutions
            active_progress_values = [ data.get("progress",0) for data in tasks.values()]
            overall_progress = sum(active_progress_values)/ len(active_progress_values) if active_progress_values else 0

            return{
                "task_id":task_id,
                "state":"Processing",
                "overall_progress":int(overall_progress),
                "details":tasks
            }

        elif result.state == "SUCCESS":
            result_data = result.info if isinstance(result.info,dict) else {}
            final_status = result_data.get("status","COMPLETED")
            tasks = result_data.get("tasks",{})

            downloads = {res: f"/tasks/{task_id}/download/{res}" for res,data in tasks.items() if data.get("status") == "COMPLETED" }
            return {
                "task_id":task_id,
                "state":final_status,
                "overall_progress":100,
                "download_urls":downloads,
                "details":tasks
            }
        elif result.state == "FAILURE":
            progress_data = result.info if isinstance(result.info,dict) else {}
            return {
                "task_id":task_id,
                "state":"Failed",
                "overall_progress":0,
                "error":progress_data.get("error","Error occured"),
                "details":progress_data.get("tasks",{})
            }
    except (ValueError,TypeError,KeyError) as e:
        logger.error(f"Corrupted task data for {task_id}:{e}")
        return {
            "task_id": task_id,
            "state": "Failed (Data Corrupted)",
            "progress": 0,
            "error": "Task data is unreadable. Please retry the upload."
        }
    
    except Exception as e:
        logger.error(f"API Error:{e}")
        raise HTTPException(status_code=500,detail="Internal Server Error")
    
    return {
        "task_id": task_id,
        "state": current_state,
        "overall_progress": 0
    }
    
