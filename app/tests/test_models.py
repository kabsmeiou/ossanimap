# create tests for db models

from types import SimpleNamespace
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.db.base import Base
from app.db.models.anime import AnimeDB
from app.db.models.pack import PackDB

@pytest.fixture()
def db_session():
    """Create a new database session with an in-memory SQLite DB for each test."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def make_anime(id=None, name="Test Anime", slug="test-anime", synopsis="syn"):
    return SimpleNamespace(id=id, name=name, slug=slug, synopsis=synopsis)

def make_pack(name="Test Pack", beatmapset_ids=None, downloads=0):
    if beatmapset_ids is None:
        beatmapset_ids = [1, 2, 3]
    return SimpleNamespace(name=name, beatmapset_ids=beatmapset_ids, downloads=downloads)

def test_create_anime_and_pack(db_session):
    anime = make_anime(id=1, name="My Anime", slug="my-anime", synopsis="an overview")
    pack = make_pack(name="My Pack", beatmapset_ids=[10, 20, 30], downloads=0)

    anime_db = AnimeDB(
        id=anime.id,
        name=anime.name,
        slug=anime.slug,
        synopsis=anime.synopsis
    )
    db_session.add(anime_db)
    db_session.flush()  # to assign ID if needed

    pack_db = PackDB(
        name=pack.name,
        anime_id=anime_db.id,
        beatmapset_ids=pack.beatmapset_ids,
    )
    db_session.add(pack_db)
    db_session.commit()

    # Retrieve and verify
    retrieved_pack = db_session.get(PackDB, pack_db.id)
    assert retrieved_pack is not None
    assert retrieved_pack.name == "My Pack"
    assert retrieved_pack.anime_id == anime_db.id
    assert retrieved_pack.beatmapset_ids == [10, 20, 30]


def test_anime_unique_slug_constraint(db_session):
    anime1 = AnimeDB(name="Anime One", slug="unique-slug", synopsis="first anime")
    anime2 = AnimeDB(name="Anime Two", slug="unique-slug", synopsis="second anime")

    db_session.add(anime1)
    db_session.commit()

    db_session.add(anime2)
    with pytest.raises(IntegrityError):
        db_session.commit()  # should raise due to unique constraint

def test_pack_foreign_key_constraint(db_session):
    pack = PackDB(name="Orphan Pack", anime_id=9999, beatmapset_ids=[1, 2, 3])  # non-existent anime_id

    db_session.add(pack)
    with pytest.raises(IntegrityError):
        db_session.commit()  # should raise due to foreign key constraint

def test_create_pack_without_anime(db_session):
    pack = PackDB(name="No Anime Pack", anime_id=None, beatmapset_ids=[1, 2, 3])

    db_session.add(pack)
    with pytest.raises(Exception):
        db_session.commit()  # should raise due to NOT NULL constraint