from pydantic import BaseModel
from typing import List, Optional, Any

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
    mode: int
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

class Availability(BaseModel):
    download_disabled: bool
    more_information: Optional[str] = None

class Genre(BaseModel):
    id: int
    name: str

class Language(BaseModel):
    id: int
    name: str

class NominationSummary(BaseModel):
    current: int
    required: int

class Beatmapset(BaseModel):
    id: int
    artist: str
    availability: Availability
    beatmaps: List[Beatmap]
    bpm: float
    can_be_hyped: bool
    converts: List[Any]
    creator: str
    current_nominations: List[Any]
    deleted_at: Optional[str] = None
    description: Any
    discussion_enabled: bool
    discussion_locked: bool
    favourite_count: int
    genre: Genre
    has_favourited: Optional[bool] = None
    hype: Any
    is_scoreable: bool
    language: Language
    last_checked: int
    last_updated: int
    nominations_summary: NominationSummary
    nsfw: bool
    offset: int
    pack_tags: List[str]
    play_count: int
    ranked: int
    ranked_date: int
    rating: float
    ratings: List[float]
    related_users: List[Any]
    source: str
    spotlight: bool
    status: str
    storyboard: bool
    submitted_date: int
    tags: List[str]
    title: str
    title_unicode: str
    track_id: Optional[int] = None
    user_id: int
    video: bool