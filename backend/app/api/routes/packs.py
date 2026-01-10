from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.services import list_packs as list_packs_from_db, delete_pack as delete_pack_from_db, increment_pack_downloads, get_pack_by_id
from app.schemas.pack import Pack, PackCreateRequest, PackResponse
from app.services.pack_generator import pack_generator, PackGenerationError
from app.utils.format import packdb_to_packschema
from app.db.session import get_session
from app.utils.helpers import create_anime_schema

router = APIRouter(
    prefix="/packs",
    tags=["packs"]
)

logger = logging.getLogger("uvicorn.error")

@router.post("/", response_model=PackResponse, status_code=status.HTTP_201_CREATED)
async def create_pack(request: PackCreateRequest, session: AsyncSession = Depends(get_session)):
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
    try:
        anime_schema = await create_anime_schema(
            id=request.anime.id,
            name=request.anime.name,
            slug=request.anime.slug,
            synopsis=request.anime.synopsis,
        )
        pack = await pack_generator.generate_pack_from_anime(
            session=session,
            anime=anime_schema,
            status=request.status,
            mode=request.mode
        )
        logger.info(pack.image_link)
        return PackResponse(
            success=True,
            message=f"Pack created successfully for {request.anime.name}",
            pack=pack
        )
    except PackGenerationError as e:
        logger.exception(f"Pack generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error msg: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pack: {str(e)}"
        )

@router.get("/", response_model=List[Pack])
async def list_packs(session: AsyncSession = Depends(get_session)):
    """
    List all available beatmap packs.
    
    Returns:
        List of all Pack objects
    """
    packs_db = await list_packs_from_db(session=session)
    packs = [packdb_to_packschema(p) for p in packs_db]
    return packs

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