from pydantic import BaseModel, field_validator
from typing import List, Optional, Any, Union

# Mode mapping for string to int conversion, according to chimu.moe(discord)
MODE_MAP = {
    "all": -1,
    "osu": 0,
    "taiko": 1,
    "ctb": 2,
    "mania": 3,
}

# next: omit fields that are not necessary for basic beatmapset info
class Beatmap(BaseModel):
    accuracy: float
    ar: float
    beatmapset_id: int
    bpm: float
    checksum: str
    convert: bool
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    deleted_at: Optional[str] = None
    difficulty_rating: float
    drain: float
    exited: Optional[int] = None
    failed: Optional[int] = None
    hit_length: int
    id: int
    is_scoreable: bool
    mode: Union[int, str]  # Can be "osu", "taiko", "fruits", "mania" or 0-3
    mode_int: int
    passcount: int
    playcount: int
    ranked: int
    status: str
    total_length: int
    url: str
    user_id: Optional[int] = None
    version: str
    last_checked: int
    last_updated: int
    max_combo: Optional[int] = None
    
    @field_validator('mode', mode='before')
    @classmethod
    def convert_mode(cls, v):
        """Convert mode string to integer if needed"""
        if isinstance(v, str):
            return MODE_MAP.get(v.lower(), 0)
        return v

class Availability(BaseModel):
    download_disabled: bool
    more_information: Optional[str] = None

class Genre(BaseModel):
    id: int
    name: str

class Beatmapset(BaseModel):
    id: int
    artist: str
    availability: Availability
    beatmaps: List[Beatmap]
    converts: List[Any]
    creator: str
    favourite_count: int
    genre: Genre
    nsfw: bool
    rating: float
    ratings: List[float]
    source: str
    status: str
    tags: Union[List[str], str]  # Can be a string or list
    title: str
    title_unicode: str
    track_id: Optional[int] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def convert_tags(cls, v):
        """Convert tags string to list if needed"""
        if isinstance(v, str):
            # Split by spaces and filter empty strings
            return [tag.strip() for tag in v.split() if tag.strip()]
        return v