from ossapi import OssapiAsync
import os
from dotenv import load_dotenv
import logging

from app.schemas.osu import Beatmapset, BeatmapsetSearchMode

load_dotenv()

api = OssapiAsync(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)

logger = logging.getLogger("uvicorn.error")

async def fetch_beatmapset(beatmapset_id: int) -> Beatmapset:
    """
    Fetch beatmapset data from osu! API via Ossapi.

    Args:
        beatmapset_id: The unique beatmapset identifier
    Returns:
        Beatmapset data as a dictionary
    """
    try:
        bm_data = await api.beatmapset(beatmapset_id)
        beatmapset = Beatmapset.model_validate(bm_data, from_attributes=True)
    except Exception as e:
        logger.error(f"Error fetching beatmapset {beatmapset_id}: {str(e)}")
        raise RuntimeError(f"Failed to fetch beatmapset {beatmapset_id}") from e
    logger.info(f"Fetched beatmapset: {beatmapset}")
    return beatmapset

async def search_beatmapsets(keyword: str) -> list[Beatmapset]:
    """
    Search for beatmapsets on osu! API via Ossapi.

    Args:
        keyword: Search query (use quotes for exact match)
    Returns:
        List of matching BeatmapsetOSU objects
    """
    try:
        keyword = f'"{keyword}"'
        results = await api.search_beatmapsets(query=keyword, mode=BeatmapsetSearchMode.STANDARD.value)
        # get the beatmapsets from the results
        beatmapsets: list[Beatmapset] = [
            Beatmapset.model_validate(bm, from_attributes=True)
            for bm in results.beatmapsets
        ]
    except Exception as e:
        logger.error(f"Error searching beatmapsets with keyword '{keyword}': {str(e)}")
        raise RuntimeError(f"Failed to search beatmapsets with keyword '{keyword}'") from e
    logger.info(f"Found {len(beatmapsets)} beatmapsets for keyword '{keyword}'")
    return beatmapsets