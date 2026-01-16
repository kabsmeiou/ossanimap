from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

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