from pydantic import BaseModel, Field
from typing import Optional


# animethemes API response schema
class Anime(BaseModel):
    """
    Represents anime metadata from animethemes.moe API.
    """
    id: int = Field(..., description="Unique anime identifier")
    name: str = Field(..., description="Name of the anime")
    slug: str = Field(..., description="Slug identifier for the anime")
    image_link: Optional[str] = Field(default=None, description="Link to the anime image")


