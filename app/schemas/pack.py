from typing import List, Optional
from pydantic import BaseModel, Field


class Pack(BaseModel):
    """
    Represents a collection of osu! beatmapsets grouped by anime.
    """
    id: int = Field(..., description="Unique pack identifier")
    name: str = Field(..., description="Human-readable pack name")
    anime_title: str = Field(..., description="Title of the anime")
    anime_slug: str = Field(..., description="URL-friendly anime identifier")
    synopsis: Optional[str] = Field(default=None, description="Brief synopsis of the anime")
    beatmapset_ids: List[int] = Field(..., description="List of beatmapset IDs in this pack")
    beatmapset_count: int = Field(..., description="Total number of beatmapsets")
    downloads: int = Field(default=0, description="Number of times this pack has been downloaded")
    artifact_url: Optional[str] = Field(default=None, description="URL to the packaged artifact in cloud storage")
    created_at: Optional[str] = Field(..., description="ISO 8601 timestamp of pack creation")
    updated_at: Optional[str] = Field(..., description="ISO 8601 timestamp of last update")

class PackCreate(BaseModel):
    """
    Model for creating a new Pack.
    """
    name: str = Field(..., description="Human-readable pack name")
    anime_title: str = Field(..., description="Title of the anime")
    anime_slug: str = Field(..., description="URL-friendly anime identifier")
    synopsis: Optional[str] = Field(default=None, description="Brief synopsis of the anime")
    beatmapset_ids: List[int] = Field(..., description="List of beatmapset IDs in this pack")


class PackCreateRequest(BaseModel):
    """
    Request model for creating a new pack.
    """
    anime_name: str = Field(..., description="Name of the anime to create a pack for")
    status: int = Field(default=1, description="Beatmap status: 1=ranked, 2=loved")
    mode: Optional[int] = Field(default=0, description="Game mode: 0=standard, 1=taiko, 2=catch, 3=mania, None=all")


class PackResponse(BaseModel):
    """
    Response model for pack operations.
    """
    success: bool
    message: str
    pack: Optional[Pack] = None
