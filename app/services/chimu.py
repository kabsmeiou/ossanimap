from typing import List, Optional
import httpx
from app.schemas.osu import Beatmapset

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
        
        response = client.get("api/v2/search", params=params)
        response.raise_for_status()
        data = response.json()
    
    return [Beatmapset(**item) for item in data]


def download_beatmapset(beatmapset_id: int) -> bytes:
    with httpx.Client(base_url=CHIMU_URL) as client:
        response = client.get(f"d/{beatmapset_id}")
        response.raise_for_status()
    return response.content

# next
# downloading beatmapsets
# getting anime metadata from animetheme
# omitting unnecessary fields in schemas
# setting up models for database storage
# caching results
# artifact packaging
# dealing with rate limits
# error handling and retries
