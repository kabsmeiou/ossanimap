from pydantic import BaseModel, Field
from typing import Any, List, Optional, Union
import enum

# Mode mapping for string to int conversion, according to chimu.moe(discord)
# for now, only use std
class BeatmapsetSearchMode(enum.Enum):
    ANY: int = -1
    STANDARD: int = 0
    TAIKO: int = 1
    CATCH: int = 2
    MANIA: int = 3

class Beatmap(BaseModel):
    beatmapset_id: int = Field(..., description="beatmapset_id")
    difficulty_rating: float = Field(..., description="difficulty_rating")
    id: int = Field(..., description="id")
    mode: Union[int, str] = Field(..., description="mode")
    mode_int: int = Field(..., description="osu game mode")
    status: str = Field(..., description="status of the beatmap")
    total_length: int = Field(..., description="total length of the beatmap in seconds")
    url: str = Field(..., description="URL to the beatmap")

class Availability(BaseModel):
    download_disabled: bool = Field(..., description="download_disabled")
    more_information: Optional[str] = Field(None, description="more information about availability")

# TODO. id is the same as osu! so we can just fetch from osu! api
# for fresher data. chimu.moe can then handle downloading
class Beatmapset(BaseModel):
    id: int = Field(..., description="beatmapset id")
    artist: str = Field(..., description="artist")
    availability: Availability = Field(..., description="availability")
    beatmaps: List[Beatmap] = Field(..., description="beatmaps in the beatmapset")
    genre: Any = Field(..., description="genre")
    nsfw: bool = Field(..., description="if the beatmapset contains NSFW")
    source: str = Field(..., description="source")
    status: str = Field(..., description="status")
    title: str = Field(..., description="title")
    title_unicode: str = Field(..., description="title in unicode")
    track_id: Optional[int] = Field(None, description="track_id")
    play_count: int = Field(..., description="number of plays")
    favourite_count: int = Field(..., description="number of favourites")