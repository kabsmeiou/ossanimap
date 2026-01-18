from app.schemas.anime import Anime

def create_dummy_anime() -> Anime:
    """Creates a dummy Anime schema instance for testing."""
    return Anime(
        id=0,
        name="Dummy Anime",
        slug="dummy-anime",
        image_link=None
    )