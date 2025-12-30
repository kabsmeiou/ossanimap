from fastapi import APIRouter
from app.services.chimu import search_for_beatmaps

router = APIRouter(
    prefix="/beatmaps",
)

@router.get("/search/")
def search_beatmaps(keyword: str):
    results = search_for_beatmaps(keyword)
    return results