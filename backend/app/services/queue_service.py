from worker.tasks.transcode import transcode_video

def enqueue_transcode_task(job_id:str,file_path:str):
    transcode_video.apply_async(
        args=[job_id,file_path],
        task_id=job_id
    )   