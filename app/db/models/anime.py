from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from ..base import Base

class AnimeDB(Base):
    __tablename__ = "anime"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    packs: Mapped[List["PackDB"]] = relationship(back_populates="anime")