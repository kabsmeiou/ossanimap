import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.main as app_main
from app.db.base import Base
from app.db import services as db_services
import app.api.routes.packs as packs_route
import app.utils.format as format_utils


@pytest.fixture()
def db_session(monkeypatch):
    # ensure models are imported so they are registered with Base.metadata
    import app.db.models.anime  # noqa: F401
    import app.db.models.pack  # noqa: F401

    from sqlalchemy.pool import StaticPool

    # Use StaticPool + check_same_thread=False so the in-memory SQLite DB can be
    # shared across threads created by TestClient
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    # monkeypatch SessionLocal used by packs route and format util so they use our test DB
    monkeypatch.setattr(packs_route, "SessionLocal", SessionLocal)
    monkeypatch.setattr(format_utils, "SessionLocal", SessionLocal)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def make_anime_meta(id=None, name="API Anime", slug="api-anime", synopsis="syn"):
    return SimpleNamespace(id=id, name=name, slug=slug, synopsis=synopsis)


def make_pack_obj(name="API Pack", synopsis="pack syn", beatmapset_ids=None, downloads=0):
    if beatmapset_ids is None:
        beatmapset_ids = [11, 22]
    # create a minimal Pack-like object with attributes expected by save_pack
    return SimpleNamespace(name=name, synopsis=synopsis, beatmapset_ids=beatmapset_ids, downloads=downloads)


def test_packdb_to_packschema_and_list_get_delete(db_session):
    # populate DB via service
    anime_meta = make_anime_meta(id=1, name="List Anime", slug="list-anime", synopsis="synopsis")
    pack_obj = make_pack_obj(name="List Pack", beatmapset_ids=[101, 202], downloads=3)

    db_services.save_pack(db_session, anime_meta, pack_obj)

    # ensure packs_route uses our DB (reset cache)
    packs_route.packs_storage = None

    client = TestClient(app_main.app)

    # List packs
    resp = client.get("/packs/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1

    pack = data[0]
    assert pack["anime_title"] == "List Anime"
    assert pack["beatmapset_ids"] == [101, 202]

    # retrieve DB id for subsequent get/delete operations
    pack_db = db_services.list_packs(db_session)[0]
    pack_id = pack_db.id

    # Get pack by id
    resp2 = client.get(f"/packs/{pack_id}")
    assert resp2.status_code == 200
    p2 = resp2.json()
    # Pack schema does not include DB id; validate returned content instead
    assert p2["anime_title"] == "List Anime"
    assert p2["beatmapset_ids"] == [101, 202]

    # Delete pack
    del_resp = client.delete(f"/packs/{pack_id}")
    assert del_resp.status_code == 204

    # List again should be empty
    packs_route.packs_storage = None
    resp3 = client.get("/packs/")
    assert resp3.status_code == 200
    assert resp3.json() == []
