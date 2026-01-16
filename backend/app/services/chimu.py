from typing import List, Optional
import httpx
import logging
import json

from app.schemas.osu import Beatmapset

logger = logging.getLogger(__name__)

CHIMU_URL = "https://catboy.best/"


async def check_chimu_api() -> dict:
    """
    Test connection to chimu.moe mirror.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    async with httpx.AsyncClient(base_url=CHIMU_URL, timeout=5.0) as client:
        try:
            response = await client.get("/api/ratelimits")
            body = await response.aread()
            resp = json.loads(body)
            return resp
        except httpx.RequestError as e:
            logger.error(f"Chimu.moe connection test failed: {str(e)}")
            return {"limits": {}}
        except httpx.HTTPStatusError as e:
            logger.error(f"Chimu.moe returned error status: {str(e)}")
            return {"limits": {}}


# status: 1 = ranked, 2 = loved, mode: 0 = osu!standard, 1 = taiko, 2 = catch, 3 = mania
async def search_for_beatmaps(
    keyword: str, 
    status: List[int] = [1], 
    mode: Optional[List[int]] = [0]
) -> List[Beatmapset]:
    """
    Search for beatmapsets on chimu.moe mirror.
    
    Args:
        keyword: Search query (use quotes for exact match)
        status: Beatmap status (1=ranked, 2=loved)
        mode: Game mode filter (0=standard, 1=taiko, 2=catch, 3=mania, None=all modes)
    
    Returns:
        List[Beatmapset]: List of matching beatmapsets
    """
    # TODO. handle queries for multiple modes/statuses
    async with httpx.AsyncClient(base_url=CHIMU_URL, timeout=5.0) as client:
        # Build query parameters
        params = {
            "q": keyword,
            "status": status[0], 
            "mode": mode[0]
        }
        try:
            response = await client.get("api/v2/search", params=params)
        except httpx.RequestError as e:
            raise RuntimeError("Chimu.moe search request failed") from e
        response.raise_for_status()
        body = await response.aread()
        data = json.loads(body)
    
    return [Beatmapset(**item) for item in data]