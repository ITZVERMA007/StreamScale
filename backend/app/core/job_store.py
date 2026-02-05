jobs = {}

def create_job(task_id:str,filename:str):
    jobs[task_id] = {
        "filename":filename,
        "task_id":task_id,  
        "status":"Uploaded",
        "progress":0
    }

def get_job(task_id:str):
    return jobs.get(task_id)