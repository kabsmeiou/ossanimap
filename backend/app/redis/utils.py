from .queue import redis_conn
from rq.job import Job

def fetch_job_instance(job_id: str) -> bool:
    """
    Fetch a job instance from Redis by its ID.

    Args:
        job_id: The unique identifier of the job.
    Returns:
        True if the job exists, False otherwise.
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return True
    except Exception:
        return False