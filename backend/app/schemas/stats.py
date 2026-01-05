from pydantic import BaseModel, Field

class Stats(BaseModel):
    """
    Represents various statistics related to packs and beatmapsets.
    """
    total_packs: int = Field(..., description="Total number of packs available")
    total_beatmapsets: int = Field(..., description="Total number of beatmapsets across all packs")
    total_downloads: int = Field(..., description="Total number of downloads across all packs")
    total_redirects: int = Field(..., description="Total number of completed redirects for pack downloads")