import os
import subprocess
import re
import logging
import sys
from app.core.celery_app import celery_app
from worker.tasks.ffmpeg import RESOLUTIONS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

OUTPUT_DIR = "/data/processed"

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
@celery_app.task(bind=True)
def transcode_video(self, job_id: str, file_path: str):

    try:
        logger.info(f"Received Job {job_id}: Processing {file_path}")

        if not os.path.exists(file_path):
            error_msg = f"Input file not found: {file_path}"
            logger.error(error_msg)
            self.update_state(state='FAILURE', meta={'error': error_msg})
            raise FileNotFoundError(error_msg)

        total_duration = get_video_duration(file_path)
        if total_duration == 0:
            logger.warning("Could not determine the video duration. Progress bar might be inaccurate.")
            total_duration = 1 

        progress_tracker = {res:{"progress":0,"status":"QUEUED","error":None} 
                            for res in RESOLUTIONS.keys()
                            }
        self.update_state(state="PROGRESS",meta={"tasks":progress_tracker})

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        for res_name,res_scale in RESOLUTIONS.items():

            output_filename = f"{job_id}_{res_name}.mp4"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            
            cmd = [
                "ffmpeg", 
                "-y",                 
                "-i", file_path,          
                "-vf", f"scale={res_scale}",  
                "-c:a", "copy",           
                '-preset', 'veryfast', 
                '-threads', '0',
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

                last_percent = -1
                # Progress calculation
                for line in process.stdout:
                    match = re.search(r"out_time_ms=(\d+)", line)
                    
                    if match:
                        current_ms = int(match.group(1))
                        current_seconds = current_ms / 1000000.0
                        percent = int((current_seconds / total_duration) * 100)
                        percent = max(0, min(100, percent))

                        if percent!=last_percent:
                            progress_tracker[res_name]["progress"] = percent
                            self.update_state(
                                state='PROGRESS',
                            meta={"tasks":progress_tracker}
                            )
                            last_percent = percent

                process.wait()

                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, cmd)
                
                progress_tracker[res_name]["status"] = "COMPLETED"
                progress_tracker[res_name]["progress"] = 100

            except Exception as e:
                logger.error(f"Failed processing {res_name}:{e}")
                progress_tracker[res_name]["status"] = "FAILED"
                progress_tracker[res_name]["error"] = str(e)
            
            self.update_state(state="PROGRESS",meta={"tasks":progress_tracker})
        failed_tasks = [res for res,data in progress_tracker.items() if data["status"] == "FAILED"]

        if len(failed_tasks) == len(RESOLUTIONS):
            logger.error(f"Job {job_id} completely failed.")
            self.update_state(state="FAILURE",meta={"error":"All resolutions failed to process.","tasks":progress_tracker})
            raise Exception("All resolutions failed")
        final_status = "PARTIAL_SUCCESS" if failed_tasks else "COMPLETED"
        logger.info(f"Job {job_id} finished with status: {final_status}")

        return {
            "status":final_status,
            "job_id": job_id,
            "tasks":progress_tracker
        }

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed with exit code {e.returncode}")
        raise e  

    except Exception as e:
        logger.error(f"Unexpected error in task: {str(e)}")
        raise e