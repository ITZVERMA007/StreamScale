from worker.tasks.transcode import transcode_video

def enqueue_transcode_task(job_id:str,object_name:str):
    transcode_video.apply_async(
        args=[job_id,object_name],
        task_id=job_id
    )   