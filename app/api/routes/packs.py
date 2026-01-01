from typing import List
from fastapi import APIRouter, HTTPException, status
import logging

from app.schemas.pack import Pack, PackCreateRequest, PackResponse
from app.services.pack_generator import pack_generator, PackGenerationError

router = APIRouter(
    prefix="/packs",
    tags=["packs"]
)

logger = logging.getLogger(__name__)

# TODO: Replace with database storage
packs_storage: List[Pack] = []


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
    try:
        logger.info(f"Creating pack for anime: {request.anime_name}")
        
        # Generate the pack
        pack = pack_generator.generate_pack_from_anime(
            anime_name=request.anime_name,
            status=request.status,
            mode=request.mode
        )
        
        # Store the pack (TODO: save to database)
        packs_storage.append(pack)
        
        return PackResponse(
            success=True,
            message=f"Pack created successfully for {request.anime_name}",
            pack=pack
        )
    
    except PackGenerationError as e:
        logger.error(f"Pack generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pack: {str(e)}"
        )


@router.get("/", response_model=List[Pack])
async def list_packs():
    """
    List all available beatmap packs.
    
    Returns:
        List of all Pack objects
    """
    return packs_storage


@router.get("/{pack_id}", response_model=Pack)
async def get_pack(pack_id: int):
    """
    Get metadata for a specific pack by ID.
    
    Args:
        pack_id: The unique pack identifier
    
    Returns:
        Pack object with metadata
    """
    pack = next((p for p in packs_storage if p.id == pack_id), None)
    
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack with ID {pack_id} not found"
        )
    
    return pack


@router.get("/search/")
async def search_packs(anime_name: str):
    """
    Search for packs by anime name.
    
    Args:
        anime_name: Partial or full anime name to search for
    
    Returns:
        List of matching Pack objects
    """
    matching_packs = [
        pack for pack in packs_storage
        if anime_name.lower() in pack.anime_title.lower()
    ]
    
    return matching_packs


@router.delete("/{pack_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pack(pack_id: int):
    """
    Delete a pack by ID.
    
    Args:
        pack_id: The unique pack identifier
    """
    global packs_storage
    
    pack = next((p for p in packs_storage if p.id == pack_id), None)
    
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack with ID {pack_id} not found"
        )
    
    packs_storage = [p for p in packs_storage if p.id != pack_id]
    logger.info(f"Pack {pack_id} deleted successfully")