from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.schemas.anime import AnimeSearchResult
from app.services.animethemes import search_anime_by_name

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/anime",
    tags=["anime"]
)

@router.get("/search", response_model=List[AnimeSearchResult])
def search_anime(anime_name: str):
    """
    Search for anime by name using the AnimeThemes API.
    
    Args:
        anime_name: Name or partial name of the anime to search for 

    Returns:
        List of matching AnimeSearchResult objects
    """    
    try:
        results = search_anime_by_name(anime_name)
        return results
    except Exception as e:
        raise HTTPException(
            detail=f"Anime search failed"
        ) from e