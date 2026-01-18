from fastapi import APIRouter
import json

from app.redis.queue import redis_async
from app.schemas.stats import Stats

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

@router.get("/", response_model=Stats)
async def stream_global_stats():
    """
    Retrieve global statistics about packs and beatmapsets.

    Returns:
        Stats: An object containing various global statistics.
    """
    stats_data = json.loads(await redis_async.get("global_stats"))
    return Stats(**stats_data)