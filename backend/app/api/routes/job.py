from fastapi import APIRouter, HTTPException, status
from rq.job import Job
import logging

from app.redis.queue import redis_sync

logger = logging.getLogger("uvicorn.error")


router = APIRouter(
    prefix="/job",
    tags=["job"]
)

def _last_exc_line(exc_info: str | None) -> str | None:
    if not exc_info:
        return None
    lines = [l for l in exc_info.splitlines() if l.strip()]
    return lines[-1] if lines else None

@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_sync)
    except Exception as e:
        logging.error(f"Error fetching job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    job_status = job.get_status()
    result = job.return_value() if job.is_finished else None
    error = None
    if job.is_failed:
        error = job.meta.get("error") or _last_exc_line(job.exc_info) or "Job failed"
    return {
        "job_id": job_id,
        "status": job_status,
        "result": result,
        "error": error,
        "enqueued_at": job.enqueued_at,
        "ended_at": job.ended_at
    }