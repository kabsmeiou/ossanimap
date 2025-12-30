from pydantic import BaseModel
from typing import Optional

class Anime(BaseModel):
    id: int
    name: str
    slug: str
    year: Optional[int] = None
    season: Optional[str] = None
    media_format: Optional[str] = None
    synopsis: Optional[str] = None
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None