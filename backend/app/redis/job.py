import asyncio
from app.schemas.anime import Anime
from app.services.pack_generator import pack_generator

def generate_pack_job(
    anime_id: int, anime_name: str, anime_slug: str, anime_synopsis: str, anime_image_url: str,
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
    # convert back to Anime schema
    anime = Anime(
        id=anime_id,
        name=anime_name,
        slug=anime_slug,
        synopsis=anime_synopsis,
        image_link=anime_image_url
    )
    asyncio.run(
        pack_generator.generate_pack_from_anime(
            anime=anime,
            status=status,
            mode=mode
        )
    )