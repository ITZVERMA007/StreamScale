import os
import subprocess
import re
import logging
import sys
import time
from app.core.celery_app import celery_app
from worker.tasks.ffmpeg import RESOLUTIONS
from app.services.s3_client import s3_client, BUCKET_NAME
from contextlib import closing
from app.db.database import sessionLocal
from app.core.job_store import job_store


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

TEMP_DIR = "/tmp"
# This function helps to get the duration of the video to help in getting the progress
def get_video_duration(file_path: str):
    
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.error(f"Failed to get video duration: {e}")
        return 0.0


#This is the function which is involved in the conversion of the video
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,      # Wait 60s before first retry
    retry_backoff_max=600,       # Max 10 minutes between retries
    task_time_limit=30 * 60,     # 30 minute timeout per task
    soft_time_limit=25 * 60      # Timeout for cleanup
    )
def transcode_video(self, job_id: str, object_name: str):
    local_input_path = None

    with closing(sessionLocal()) as db:
        try:
            logger.info(f"Received Job {job_id}: Processing {object_name}")

            job_store.update_job_status(db, job_id, status="PROCESSING")

            _, ext = os.path.splitext(object_name)
            local_input_path = os.path.join(TEMP_DIR, f"{job_id}_input{ext}")
            try:
                s3_client.download_file(
                    BUCKET_NAME,
                    object_name,
                    local_input_path
                )
            except Exception as e:
                error_msg = f"Failed to download object {object_name} from S3: {str(e)}"
                logger.error(error_msg)
                raise self.retry(exc=e, countdown=60)

            total_duration = get_video_duration(local_input_path)
            if total_duration == 0:
                logger.warning("Could not determine the video duration.")
                total_duration = 1 

            progress_tracker = {res:{"progress":0,"status":"QUEUED","error":None} 
                                for res in RESOLUTIONS.keys()
                                }
            self.update_state(state="PROGRESS",meta={"tasks":progress_tracker})
            
            for res_name,res_scale in RESOLUTIONS.items():

                output_filename = f"{job_id}_{res_name}.mp4"
                output_path = os.path.join(TEMP_DIR, output_filename)

                
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i", local_input_path,
                    "-vf", f"scale={res_scale}",
                    "-c:v", "libx264",
                    "-c:a", "copy",
                    "-preset", "veryfast",
                    "-threads", "2",              # Limit threads to prevent OOM
                    "-max_muxing_queue_size", "1024",  # Prevent buffering overflow
                    "-progress", "pipe:1",
                    output_path
                ]

                logger.info(f"Running FFmpeg command for {res_name}: {' '.join(cmd)}")
                try:
                # Start the process without blocking using Popen
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT, 
                        universal_newlines=True   
                    )
                    last_update_time = time.time()
                    last_percent = -1
                    min_update_interval = 2.0

                    # Progress calculation
                    for line in process.stdout:
                        match = re.search(r"out_time_ms=(\d+)", line)
                        
                        if match:
                            current_ms = int(match.group(1))
                            current_seconds = current_ms / 1000000.0
                            percent = int((current_seconds / total_duration) * 100)
                            percent = max(0, min(100, percent))

                            current_time = time.time()
                            if (percent!=last_percent and percent % 5 == 0) or \
                                (current_time - last_update_time >= min_update_interval):
                                progress_tracker[res_name]["progress"] = percent
                                self.update_state(
                                    state='PROGRESS',
                                    meta={"tasks":progress_tracker}
                                )
                                last_percent = percent
                                last_update_time = current_time

                    process.wait()

                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(process.returncode, cmd)
                    
                    progress_tracker[res_name]["status"] = "COMPLETED"
                    progress_tracker[res_name]["progress"] = 100

                    # Uploading finished file to S3
                    s3_client.upload_file(
                        output_path,
                        BUCKET_NAME,
                        f"output/{output_filename}"
                    )
                    logger.info(f"Uploaded {output_filename} to S3")

                except Exception as e:
                    logger.error(f"Failed processing {res_name}:{e}")
                    progress_tracker[res_name]["status"] = "FAILED"
                    progress_tracker[res_name]["error"] = str(e)

                finally:
                    # Always clean up output temp file, even on failure
                    try:
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            logger.info(f"Cleaned up temp file: {output_filename}")
                    except OSError as cleanup_error:
                        logger.warning(f"Could not clean up temp file {output_filename}: {cleanup_error}")

                    self.update_state(state="PROGRESS",meta={"tasks":progress_tracker})
            failed_tasks = [res for res,data in progress_tracker.items() if data["status"] == "FAILED"]

            if len(failed_tasks) == len(RESOLUTIONS):
                logger.error(f"Job {job_id} completely failed.")
                self.update_state(state="FAILURE",meta={"error":"All resolutions failed to process."})

                job_store.update_job_status(db,job_id,status="FAILED",is_completed=True)
                raise Exception("All resolutions failed")
            
            final_status = "PARTIAL_SUCCESS" if failed_tasks else "COMPLETED"
            logger.info(f"Job {job_id} finished with status: {final_status}")

            # Database updation
            db_status = "SUCCESS" if final_status == "COMPLETED" else "FAILED"
            job_store.update_job_status(db,job_id,status=db_status,is_completed=True)

            return {
                "status":final_status,
                "job_id": job_id,
                "tasks":progress_tracker
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed with exit code {e.returncode}")
            job_store.update_job_status(db,job_id,status="FAILED",is_completed=True)
            raise e  

        except Exception as e:
            logger.error(f"Unexpected error in task: {str(e)}")
            job_store.update_job_status(db,job_id,status="FAILED",is_completed=True)
            raise e

        finally:
            # Always clean up the input file, regardless of success or failure
            if local_input_path:
                try:
                    if os.path.exists(local_input_path):
                        os.remove(local_input_path)
                        logger.info(f"Cleaned up input file: {os.path.basename(local_input_path)}")
                except OSError as e:
                    logger.warning(f"Could not clean up input file {local_input_path}: {e}")