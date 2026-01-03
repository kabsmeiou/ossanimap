from sqlalchemy import ARRAY, ForeignKey, String, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from .anime import AnimeDB
from .base import Base

class PackDB(Base):
    __tablename__ = "packs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    anime_id: Mapped[int] = mapped_column(ForeignKey("animes.id"), nullable=False)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    beatmapset_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False)
    downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    artifact_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )

    anime: Mapped[AnimeDB] = relationship()
