from sqlalchemy import ARRAY, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import List, Optional

class PackDB(Base):  # type: ignore
    __tablename__ = "packs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    anime_id: Mapped[int] = mapped_column(Integer, nullable=False)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    beatmapset_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False)
    downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    artifact_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now(datetime.timezone.utc), nullable=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now(datetime.timezone.utc),
        onupdate=datetime.now(datetime.timezone.utc),
        nullable=True
    )