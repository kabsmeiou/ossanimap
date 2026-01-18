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