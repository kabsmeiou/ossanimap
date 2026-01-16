from sqlalchemy import JSON, ForeignKey, String, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from .anime import AnimeDB
from ..base import Base

class PackDB(Base):
    __tablename__ = "pack"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"), nullable=False)
    # store beatmapset and status IDs as JSON for DB portability (works on SQLite/Postgres)
    beatmapset_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    # same mapping as chimu at schemas/osu.py
    mode: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=0)
    status: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=1)
    downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )

    # relationship
    anime: Mapped[AnimeDB] = relationship(back_populates="packs", lazy="joined")

    # packs should be unique per anime, mode, and status combination
    __table_args__ = (
        UniqueConstraint("anime_id", "mode", "status", name="uix_anime_mode_status"),
    )

    @property
    def beatmapset_count(self) -> int:
        return len(self.beatmapset_ids) if self.beatmapset_ids else 0
