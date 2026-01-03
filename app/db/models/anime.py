from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .base import Base

class AnimeDB(Base):
    __tablename__ = "animes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)