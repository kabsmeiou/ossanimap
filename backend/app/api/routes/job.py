from fastapi import APIRouter, HTTPException, status
from rq.job import Job
import logging

from app.redis.queue import redis_sync

logger = logging.getLogger("uvicorn.error")


router = APIRouter(
    prefix="/job",
    tags=["job"]
)

@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_sync)
        job_status = job.get_status()
        result = job.return_value()
        return {
            "job_id": job_id,
            "status": job_status,
            "result": result,
            "enqueued_at": job.enqueued_at,
            "ended_at": job.ended_at
        }
    except Exception as e:
        logging.error(f"Error fetching job {job_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")