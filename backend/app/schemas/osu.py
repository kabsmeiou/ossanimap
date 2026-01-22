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

class Availability(BaseModel):
    download_disabled: bool = Field(..., description="download_disabled")
    more_information: Optional[str] = Field(None, description="more information about availability")

class Beatmapset(BaseModel):
    id: int = Field(..., description="beatmapset id")
    title: str = Field(..., description="title")
    title_unicode: str = Field(..., description="title in unicode")
    source: str = Field(..., description="source")
    status: str = Field(..., description="status")