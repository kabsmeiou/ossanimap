from .models.anime import AnimeDB
from .models.pack import PackDB

def save_pack(session, anime_metadata, pack):
    """Saves the Pack and associated Anime to the database."""
    anime_db = AnimeDB(
        name=anime_metadata.name,
        slug=anime_metadata.slug,
        synopsis=anime_metadata.synopsis
    )
    session.add(anime_db)
    session.flush()  # assign anime_db.id without committing

    pack_db = PackDB(
        name=pack.name,
        anime_id=anime_db.id,
        synopsis=pack.synopsis,
        beatmapset_ids=pack.beatmapset_ids,
        downloads=pack.downloads,
    )
    session.add(pack_db)
    session.commit()
