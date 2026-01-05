from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.stats import Stats
from app.db.session import get_session
from app.db.services import get_global_stats

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

@router.get("/", response_model=Stats)
def read_global_stats(db=Depends(get_session)):
    """
    Retrieve global statistics about packs and beatmapsets.

    Returns:
        Stats: An object containing various global statistics.
    """
    try:
        stats = get_global_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve global stats: {str(e)}"
        )