from typing import List
from app.schemas.anime import Anime
import logging

logger = logging.getLogger("uvicorn.error")

def extract_anime_data_from_search(data: List[dict]) -> List[Anime]:
    """
    Extract relevant anime data from the raw anime dictionary.

    Args:
        anime: Raw anime or list of raw anime dictionaries from animethemes API.
    """
    anime_list = data.get("anime", [])
    # loop through anime and get only 1 facet="Large Cover" image
    for anime in anime_list:
        images = anime.get("images", [])
        large_cover_image = None
        for image in images:
            if image.get("facet") == "Large Cover":
                large_cover_image = image
                break
        anime["image_link"] = large_cover_image.get("link") if large_cover_image else None
    return [Anime(**anime) for anime in anime_list]
