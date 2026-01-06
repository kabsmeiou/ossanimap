import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_session
from app.db import services as db_services


@pytest.fixture()
def db_session():
    """Create a new database session with an in-memory SQLite DB for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """Create a test client with a database session override."""
    def override_get_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_anime_metadata(name="Test Anime", slug="test-anime", synopsis="A test synopsis"):
    return SimpleNamespace(name=name, slug=slug, synopsis=synopsis)


def make_pack_obj(name="Test Pack", beatmapset_ids=None):
    if beatmapset_ids is None:
        beatmapset_ids = [1, 2, 3]
    return SimpleNamespace(name=name, beatmapset_ids=beatmapset_ids)


def test_get_global_stats(client, db_session):
    """Test the /stats/ endpoint returns correct statistics."""
    # Create test data
    anime1 = make_anime_metadata(name="Anime 1", slug="anime-1")
    pack1 = make_pack_obj(name="Pack 1", beatmapset_ids=[1, 2, 3])
    pack1_db = db_services.save_pack(db_session, anime1, pack1)
    
    anime2 = make_anime_metadata(name="Anime 2", slug="anime-2")
    pack2 = make_pack_obj(name="Pack 2", beatmapset_ids=[4, 5, 6, 7])
    pack2_db = db_services.save_pack(db_session, anime2, pack2)
    
    db_session.commit()
    
    # Add some downloads
    db_services.increment_pack_downloads(db_session, pack1_db.id)
    db_services.increment_pack_downloads(db_session, pack1_db.id)
    db_services.increment_pack_downloads(db_session, pack2_db.id)
    
    # Call the endpoint
    response = client.get("/stats/")
    print(response.json())
    # Assert response
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_packs"] == 2
    assert data["total_beatmapsets"] == 7  # 3 + 4
    assert data["total_downloads"] == 3  # 2 + 1
