from typing import List, Optional
import httpx
from app.schemas.osu import Beatmapset
import logging

logger = logging.getLogger(__name__)

CHIMU_URL = "https://catboy.best/"

# status: 1 = ranked, 2 = loved, mode: 0 = osu!standard, 1 = taiko, 2 = catch, 3 = mania
def search_for_beatmaps(
    keyword: str, 
    status: int = 1, 
    mode: Optional[int] = 0
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
    with httpx.Client(base_url=CHIMU_URL, timeout=5.0) as client:
        # Build query parameters
        params = {"q": keyword, "status": status}
        if mode is not None:
            params["mode"] = mode
        try:
            response = client.get("api/v2/search", params=params)
        except httpx.RequestError as e:
            raise ("Chimu.moe search request failed") from e
        response.raise_for_status()
        data = response.json()
    
    return [Beatmapset(**item) for item in data]