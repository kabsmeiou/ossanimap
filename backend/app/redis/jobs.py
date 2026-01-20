import asyncio
import logging

from .queue import redis_async
from app.schemas.anime import Anime
from app.services.pack_generator import pack_generator
from app.db.session import AsyncSessionLocal
from app.db.services import get_global_stats

# Log the exception
logger = logging.getLogger(__name__)


def generate_pack_job(
    anime_id: int, anime_name: str, anime_slug: str, anime_image_link: str,
    status: list[int], mode: list[int]
):
    """
    Enqueue a pack generation job.

    Args:
        job_id: Unique identifier for the job
        anime: Anime schema object
        status: List of status codes for the pack
        mode: List of mode codes for the pack
    """
    # create anime schema
    anime = Anime(
        id=anime_id,
        name=anime_name,
        slug=anime_slug,
        image_link=anime_image_link
    )
    pack_id = asyncio.run(
        pack_generator.generate_pack_from_anime(
            anime=anime,
            status=status,
            mode=mode
        )
    )
    logger.info(f"Pack generation job completed for anime {anime.name}, pack ID: {pack_id}")
    return pack_id

async def stats_updater():
    """
    Periodically update global statistics in Redis.
    """
    try:
        while True:
            async with AsyncSessionLocal() as session:
                stats = await get_global_stats(session)
            
            await redis_async.set("global_stats", stats.model_dump_json())
            await asyncio.sleep(10)  # update cache every 3 seconds
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.error(f"Stats updater encountered an error: {e}")
        # Optionally, you can choose to restart the loop or handle the error as needed