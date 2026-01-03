from pydantic import BaseModel, Field
from typing import List, Optional, Union

# Mode mapping for string to int conversion, according to chimu.moe(discord)
MODE_MAP = {
    "all": -1,
    "osu": 0,
    "taiko": 1,
    "ctb": 2,
    "mania": 3,
}

# next: omit fields that are not necessary for basic beatmapset info
class BeatmapSchema(BaseModel):
    beatmapset_id: int = Field(..., description="beatmapset_id")
    difficulty_rating: float = Field(..., description="difficulty_rating")
    id: int = Field(..., description="id")
    mode: Union[int, str] = Field(..., description="mode") # Can be "osu", "taiko", "fruits", "mania" or 0-3
    mode_int: int = Field(..., description="osu game mode")
    status: str = Field(..., description="status of the beatmap")
    total_length: int = Field(..., description="total length of the beatmap in seconds")
    url: str = Field(..., description="URL to the beatmap")

class Availability(BaseModel):
    download_disabled: bool = Field(..., description="download_disabled")
    more_information: Optional[str] = Field(None, description="more information about availability")

class Genre(BaseModel):
    id: int = Field(..., description="genre id")
    name: str = Field(..., description="genre name")

class Beatmapset(BaseModel):
    id: int = Field(..., description="beatmapset id")
    artist: str = Field(..., description="artist")
    availability: Availability = Field(..., description="availability")
    beatmaps: List[Beatmap] = Field(..., description="beatmaps in the beatmapset")
    genre: Genre = Field(..., description="genre")
    nsfw: bool = Field(..., description="if the beatmapset contains NSFW")
    source: str = Field(..., description="source")
    status: str = Field(..., description="status")
    title: str = Field(..., description="title")
    title_unicode: str = Field(..., description="title in unicode")
    track_id: Optional[int] = Field(None, description="track_id")