from sqlalchemy.orm import Session
from app.db.models import Job
from datetime import datetime

class JobStore:

    # Create and add the job in the database
    def create_job(self,db:Session,job_id:str,original_filename:str,input_object_name:str,resolutions:list=None)->Job:

        db_job = Job(
            job_id = job_id,
            original_filename = original_filename,
            input_object_name = input_object_name,
            status = "PENDING",
            resolution = resolutions or []
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job

    # Helps to return the job according to the id
    def get_job(self,db:Session,job_id:str)->Job:
        return db.query(Job).filter(Job.job_id == job_id).first()
    
    # This updates the status of the job
    def update_job_status(self,db:Session,job_id:str,status:str,is_completed:bool=False)->Job:
        db_job = self.get_job(db,job_id)
        if db_job:
            db_job.status = status

            if is_completed:
                db_job.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(db_job)
        return db_job

# A single instance which we can use globally
job_store = JobStore()