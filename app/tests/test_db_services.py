import pytest
from types import SimpleNamespace
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db import services as db_services


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


def make_anime_metadata(id=None, name="Test Anime", slug="test-anime", synopsis="syn"):
    return SimpleNamespace(id=id, name=name, slug=slug, synopsis=synopsis)


def make_pack_obj(name="Test Pack", beatmapset_ids=None, downloads=0):
    if beatmapset_ids is None:
        beatmapset_ids = [1, 2, 3]
    return SimpleNamespace(name=name, beatmapset_ids=beatmapset_ids, downloads=downloads)


def test_save_and_list_pack(db_session):
    anime_meta = make_anime_metadata(id=42, name="My Anime", slug="my-anime", synopsis="an overview")
    another_anime_meta = make_anime_metadata(id=43, name="Another Anime", slug="another-anime", synopsis="another overview")
    pack1 = make_pack_obj(name="My Pack", beatmapset_ids=[10, 20, 30], downloads=0)
    pack2 = make_pack_obj(name="My Pack 2", beatmapset_ids=[40, 50, 60], downloads=5)

    # Save packs
    db_services.save_pack(db_session, anime_meta, pack1)
    db_services.save_pack(db_session, another_anime_meta, pack2)

    # List packs
    packs = db_services.list_packs(db_session)
    assert len(packs) == 2
    p = packs[0]
    assert p.name == "My Pack"
    assert p.beatmapset_ids == [10, 20, 30]


def test_get_pack_and_anime_by_id_and_slug(db_session):
    anime_meta = make_anime_metadata(id=99, name="Another Anime", slug="another-anime", synopsis="synopsis")
    pack = make_pack_obj(name="Another Pack", beatmapset_ids=[5, 6])

    db_services.save_pack(db_session, anime_meta, pack)

    packs = db_services.list_packs(db_session)
    assert packs, "expected at least one pack"
    pack_db = packs[0]

    # get by id
    fetched = db_services.get_pack_by_id(db_session, pack_db.id)
    assert fetched is not None
    assert fetched.id == pack_db.id
    assert fetched.name == "Another Pack"

    # get anime by slug
    anime_db = db_services.get_anime_by_slug(db_session, anime_meta.slug)
    assert anime_db is not None
    assert anime_db.slug == anime_meta.slug


def test_delete_pack(db_session):
    anime_meta = make_anime_metadata(name="ToDelete", slug="todelete", id=7)
    pack = make_pack_obj(name="Delete Pack")

    db_services.save_pack(db_session, anime_meta, pack)
    packs_before = db_services.list_packs(db_session)
    assert len(packs_before) == 1

    pack_id = packs_before[0].id
    deleted = db_services.delete_pack(db_session, pack_id)
    assert deleted is True

    packs_after = db_services.list_packs(db_session)
    assert len(packs_after) == 0
