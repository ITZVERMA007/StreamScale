import os
import logging
import sys
from datetime import datetime, timedelta
from contextlib import closing
from sqlalchemy import text
from app.core.celery_app import celery_app
from app.db.database import sessionLocal
from app.db.models import Job

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

TEMP_DIR = "/tmp"


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_jobs(self):
    """
    Cleanup old job records from PostgreSQL database.
    
    Deletes:
    - Completed jobs older than 7 days
    - Failed jobs older than 3 days
    """
    try:
        with closing(sessionLocal()) as db:
            now = datetime.utcnow()
            
            # Calculate cutoff dates
            completed_cutoff = now - timedelta(days=7)
            failed_cutoff = now - timedelta(days=3)
            
            # Delete completed jobs older than 7 days
            completed_query = db.query(Job).filter(
                Job.status.in_(['SUCCESS', 'COMPLETED', 'PARTIAL_SUCCESS']),
                Job.created_at < completed_cutoff
            )
            completed_count = completed_query.count()
            completed_query.delete(synchronize_session=False)
            
            # Delete failed jobs older than 3 days
            failed_query = db.query(Job).filter(
                Job.status.in_(['FAILED']),
                Job.created_at < failed_cutoff
            )
            failed_count = failed_query.count()
            failed_query.delete(synchronize_session=False)
            
            # Commit the deletions
            db.commit()
            
            total_deleted = completed_count + failed_count
            logger.info(
                f"Database cleanup completed: "
                f"{completed_count} completed jobs (>7 days), "
                f"{failed_count} failed jobs (>3 days) deleted. "
                f"Total: {total_deleted}"
            )
            
            return {
                "status": "success",
                "completed_deleted": completed_count,
                "failed_deleted": failed_count,
                "total_deleted": total_deleted,
                "timestamp": now.isoformat()
            }
            
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def cleanup_orphaned_temp_files(self):
    """
    Cleanup temporary files in /tmp directory.
    
    Removes:
    - Files older than 24 hours matching job patterns (input/output videos)
    - Partial/unfinished ffmpeg outputs
    
    This is a safety net in case worker cleanup failed.
    """
    try:
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=24)
        
        cleaned_count = 0
        cleaned_size = 0
        
        # Patterns for temp files we create
        temp_patterns = [
            '_input',      # Downloaded input files
            '_360.mp4',    # Transcoded outputs
            '_720.mp4',
            '_1080.mp4',
        ]
        
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            
            # Check if file matches our patterns and is old enough
            if any(pattern in filename for pattern in temp_patterns):
                try:
                    stat = os.stat(filepath)
                    file_mtime = datetime.fromtimestamp(stat.st_mtime)
                    
                    if file_mtime < cutoff_time:
                        file_size = stat.st_size
                        os.remove(filepath)
                        cleaned_count += 1
                        cleaned_size += file_size
                        logger.info(f"Cleaned orphaned temp file: {filename} ({file_size} bytes)")
                        
                except (OSError, IOError) as e:
                    logger.warning(f"Could not remove temp file {filename}: {e}")
                    continue
        
        logger.info(
            f"Temp file cleanup completed: "
            f"{cleaned_count} files removed, "
            f"{cleaned_size / (1024*1024):.2f} MB freed"
        )
        
        return {
            "status": "success",
            "files_cleaned": cleaned_count,
            "bytes_freed": cleaned_size,
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Temp file cleanup failed: {e}")
        raise self.retry(exc=e)
