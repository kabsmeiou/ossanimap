from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.stats import Stats
from app.db.session import get_session
from app.db.services import get_global_stats

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

@router.get("/", response_model=Stats)
async def read_global_stats(db: AsyncSession = Depends(get_session)):
    """
    Retrieve global statistics about packs and beatmapsets.

    Returns:
        Stats: An object containing various global statistics.
    """
    stats = await get_global_stats(db)
    return stats