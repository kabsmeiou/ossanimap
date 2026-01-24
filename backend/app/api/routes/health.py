from fastapi import APIRouter, status
import logging

from app.services.animethemes import check_animethemes_api
from app.services.chimu import check_chimu_api

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify that the API is running.

    Returns:
        dict: A simple message indicating the API is healthy.
    """
    return {"status": "healthy"}

@router.get("/chimu", status_code=status.HTTP_200_OK)
async def chimu_health_check():
    """
    Health check endpoint to verify that the chimu.moe service is reachable.
    """
    response = await check_chimu_api()
    return response

@router.get("/animethemes", status_code=status.HTTP_200_OK)
async def animethemes_health_check():
    """
    Health check endpoint to verify that the AnimeThemes API is reachable.
    """
    status = await check_animethemes_api()
    if not status:
        return {"status": "-1"}
    return {"status": "1"}