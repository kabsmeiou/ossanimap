from typing import List, Optional
from pydantic import BaseModel, Field

from .anime import Anime

class Pack(BaseModel):
    """
    Represents a collection of osu! beatmapsets grouped by anime.
    """
    id: int = Field(..., description="Unique pack identifier")
    name: str = Field(..., description="Human-readable pack name")
    anime_title: str = Field(..., description="Title of the anime")
    image_link: Optional[str] = Field(default=None, description="Link to the anime image")
    status: List[int] = Field(..., description="status of beatmap in the pack: 1=ranked,2=loved")
    mode: List[int] = Field(..., description="modes of beatmap in the pack: -1=all,0=standard,1=taiko,2=catch,3=mania")
    beatmapset_ids: List[int] = Field(..., description="List of beatmapset IDs in this pack")
    beatmapset_count: int = Field(..., description="Total number of beatmapsets")
    downloads: int = Field(default=0, description="Number of times this pack has been downloaded")
    created_at: Optional[str] = Field(..., description="ISO 8601 timestamp of pack creation")
    updated_at: Optional[str] = Field(..., description="ISO 8601 timestamp of last update")

class PackCreate(BaseModel):
    """
    Model for creating a new Pack.
    """
    name: str = Field(..., description="Human-readable pack name")
    anime_id: int = Field(..., description="Unique identifier of the associated anime")
    anime_title: str = Field(..., description="Title of the anime")
    anime_slug: str = Field(..., description="Slug of the anime")
    image_link: Optional[str] = Field(default=None, description="Link to the anime image")
    status: List[int] = Field(..., description="status of beatmapsets in the pack: 1=ranked,2=loved")
    mode: List[int] = Field(..., description="modes of beatmapsets in the pack: 0=standard,1=taiko,2=catch,3=mania")

    beatmapset_ids: List[int] = Field(..., description="List of beatmapset IDs in this pack")


class PackCreateRequest(BaseModel):
    """
    Request model for creating a new pack.
    """
    anime: Anime = Field(..., description="Anime metadata for the pack")
    status: List[int] = Field(default=[1], description="Beatmap status: 1=ranked, 2=loved")
    mode: Optional[List[int]] = Field(default=[0], description="Game mode: 0=standard, 1=taiko, 2=catch, 3=mania, -1=all")

class PackResponse(BaseModel):
    """
    Response model for pack operations.
    """
    success: bool
    message: str
    job_id: Optional[str] = None

class PaginatedResponse(BaseModel):
    next_cursor: Optional[str] = Field(None, description="Cursor for the next page of results")
    items: List[Pack] = Field(..., description="List of packs on the current page")
