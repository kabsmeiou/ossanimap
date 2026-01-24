from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession
import json
import httpx
from fastapi.responses import StreamingResponse
from fastapi import Query

from app.db.services import list_packs_paginated, delete_pack as delete_pack_from_db, increment_pack_downloads, get_pack_by_id, get_beatmapset_list
from app.schemas.pack import Pack, PackCreateRequest, PackResponse, PaginatedResponse
from app.schemas.osu import Beatmapset
from app.redis.jobs import generate_pack_job
from app.utils.format import packdb_to_packschema
from app.db.session import get_session
from app.redis.queue import pack_creation_queue
from app.services.pack_generator import pack_generator
from app.services.osu import fetch_beatmapsets
from app.redis.queue import redis_sync


router = APIRouter(
    prefix="/packs",
    tags=["packs"]
)

logger = logging.getLogger("uvicorn.error")

@router.get("/img")
async def proxy_image(url: str = Query(..., description="Remote image URL")):
    if not (url.startswith("https://") or url.startswith("http://")):
        raise HTTPException(status_code=400, detail="Invalid url")

    allowed_hosts = {
        "pub-92474f7785774e91a790e086dfa6b2ef.r2.dev",  # R2 CDN for anime images
    }

    parsed = httpx.URL(url)
    if parsed.host not in allowed_hosts:
        raise HTTPException(status_code=403, detail=f"Host '{parsed.host}' not allowed")

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            r = await client.get(url)
            r.raise_for_status()
            content_type = r.headers.get("content-type", "image/*")
            # Read the full content since we can't stream after context exits
            content = await r.aread()
            from fastapi.responses import Response
            return Response(
                content=content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400"
                },
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Upstream error")
    except httpx.RequestError as e:
        logger.error(f"Request error proxying image: {e}")
        raise HTTPException(status_code=502, detail="Upstream unreachable")

@router.post("/", response_model=PackResponse, status_code=status.HTTP_201_CREATED)
async def create_pack(request: PackCreateRequest):
    """
    Create a new beatmap pack from an anime name.
    
    This endpoint:
    1. Fetches anime metadata from AnimeThemes API
    2. Searches for ranked/loved beatmapsets on chimu.moe
    3. Creates a Pack object with the collected beatmapset IDs
    
    Args:
        request: PackCreateRequest containing anime_name, status, and mode filters
    
    Returns:
        PackResponse with the created pack
    """
    job_id = pack_generator.create_job_id(
        anime_id=request.anime.id,
        status=request.status,
        mode=request.mode
    )
    # if a job with the same id is already in the queue or being processed, return its job id
    # if fetch_job_instance(job_id):
    #     return PackResponse(
    #         success=True,
    #         message=f"Pack for {request.anime.name} is already being generated",
    #         job_id=job_id
    #     )
    pack_creation_queue.enqueue(
        generate_pack_job,
        failure_ttl=10,
        job_id=job_id,
        anime_id=request.anime.id,
        anime_name=request.anime.name,
        anime_slug=request.anime.slug,
        anime_image_link=request.anime.image_link,
        status=request.status,
        mode=request.mode
    )
    return PackResponse(
        success=True,
        message=f"Pack for {request.anime.name} is being generated",
        job_id=job_id
    )

@router.get("/{pack_id}/beatmapsets", response_model=List[Beatmapset])
async def get_beatmapset_metadata(pack_id: int, session: AsyncSession = Depends(get_session)):
    # just cache for everyone so we dont have to rehit osu! every click on a pack
    cached = redis_sync.get(str(pack_id))
    if cached is None:
        beatmapset_ids = await get_beatmapset_list(session, pack_id)
        bmsets = await fetch_beatmapsets(beatmapset_ids)  # List[Beatmapset], needs to be dumpd each
        redis_sync.set(
            str(pack_id),
            json.dumps([b.model_dump() for b in bmsets]),
            ex=60 * 60 * 24
        )
    else:
        data = json.loads(cached.decode('utf-8'))
        bmsets = [Beatmapset.model_validate(x) for x in data]
    return bmsets

# TODO. create route for fetching beatmap ids for a pack_id. 
# this is to reduce the payload size of the list_packs and get_pack endpoints
# (omit beatmapset_ids field)
@router.get("/", response_model=PaginatedResponse)
async def list_packs(
    session: AsyncSession = Depends(get_session),
    cursor: Optional[str] = None,
    limit: int = 10,
    q: str = ""
):
    """
    List all available beatmap packs.
    
    Returns:
        List of all Pack objects
    """
    packs_db, next_cursor = await list_packs_paginated(
        session=session, 
        cursor=cursor, 
        limit=limit,
        query=q
    )
    packs = [packdb_to_packschema(p) for p in packs_db]
    return {
        "next_cursor": next_cursor,
        "items": packs
    }

@router.get("/{pack_id}", response_model=Pack)
async def get_pack(pack_id: int, session: AsyncSession = Depends(get_session)):
    """
    Get metadata for a specific pack by ID.
    
    Args:
        pack_id: The unique pack identifier
    
    Returns:
        Pack object with metadata
    """
    pack = await get_pack_by_id(session, pack_id)
    if pack:
        pack = packdb_to_packschema(pack)

    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack with ID {pack_id} not found"
        )
    
    return pack

# increment downloads count endpoint
@router.get("/{pack_id}/increment-downloads", status_code=status.HTTP_200_OK)
async def increment_downloads(pack_id: int, session: AsyncSession = Depends(get_session)):
    """
    Increment the download count for a specific pack by ID.
    
    Args:
        pack_id: The unique pack identifier
    """
    await increment_pack_downloads(session=session, pack_id=pack_id)
    return {"message": f"Download count incremented for pack ID {pack_id}"}

@router.delete("/{pack_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pack(pack_id: int, session: AsyncSession = Depends(get_session)):
    """
    Delete a pack by ID.
    
    Args:
        pack_id: The unique pack identifier
        session: Database session dependency
    """
    pack = await get_pack_by_id(session, pack_id)
    if not pack:
        logger.exception(f"Pack with ID {pack_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack with ID {pack_id} not found"
        )
    await delete_pack_from_db(session, pack_id)
    logger.info(f"Pack {pack_id} deleted successfully")