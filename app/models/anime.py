from pydantic import BaseModel
from typing import Optional

class Anime(BaseModel):
    id: int
    name: str
    slug: str
    year: Optional[int] = None
    season: Optional[str] = None
    media_format: str
    synopsis: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None