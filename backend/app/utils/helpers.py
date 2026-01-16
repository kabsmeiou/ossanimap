from typing import Optional
from app.schemas.anime import Anime
from app.services.animethemes import fetch_anime_image_link
import logging

logger = logging.getLogger("uvicorn.error")

async def create_anime_schema(
    id: int,
    name: str,
    slug: str,
    synopsis: Optional[str] = None,
) -> Optional[Anime]:
    """
    Create an Anime schema instance.

    Args:
        id: Unique anime identifier
        name: Name of the anime
        slug: Slug identifier for the anime
        synopsis: Synopsis of the anime
        image_link: Link to the anime image

    Returns:
        Anime: Anime schema instance
    """
    try:
        image_link = await fetch_anime_image_link(name)
    except Exception as e:
        logger.info(f"Failed to fetch anime image link for {name}: {str(e)}")
        return None
        # raise RuntimeError("Failed to fetch anime image link") from e
    return Anime(
        id=id,
        name=name,
        slug=slug,
        synopsis=synopsis,
        image_link=image_link
    )