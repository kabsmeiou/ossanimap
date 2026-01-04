from sqlalchemy import select

from .models.anime import AnimeDB
from .models.pack import PackDB


def save_pack(session, anime_metadata, pack):
    """Saves the Pack and associated Anime to the database."""
    anime_db = AnimeDB(
        name=anime_metadata.name,
        slug=anime_metadata.slug,
        synopsis=anime_metadata.synopsis
    )
    # if anime_metadata provides an ID (from external API), use it so that
    # external references remain stable; otherwise let the DB assign one
    if hasattr(anime_metadata, "id") and anime_metadata.id is not None:
        try:
            anime_db.id = int(anime_metadata.id)
        except Exception:
            # fallback: ignore provided id if it cannot be cast to int
            pass

    session.add(anime_db)
    session.flush()  # assign anime_db.id without committing

    pack_db = PackDB(
        name=pack.name,
        anime_id=anime_db.id,
        beatmapset_ids=pack.beatmapset_ids,
    )
    session.add(pack_db)
    session.flush()  # assign pack_db.id without committing

    return pack_db

def list_packs(session):
    """Lists all packs in the database."""
    stmt = select(PackDB)
    result = session.scalars(stmt).all()
    return result

def get_pack_by_id(session, pack_id):
    """Retrieves a pack by its ID."""
    stmt = select(PackDB).where(PackDB.id == pack_id)
    result = session.scalars(stmt).first()
    return result

def increment_pack_downloads(session, pack_id):
    """Increments the download count for a specific pack."""
    pack = get_pack_by_id(session, pack_id)
    if pack:
        pack.downloads += 1
        session.commit()
        return True
    return False

def get_anime_by_slug(session, slug):
    """Retrieves an anime by its slug."""
    stmt = select(AnimeDB).where(AnimeDB.slug == slug)
    result = session.scalars(stmt).first()
    return result

def delete_pack(session, pack_id) -> bool:
    """
    Deletes a pack by its ID.
    
    Returns: True if deletion was successful, False otherwise.
    """
    pack_to_delete = session.get(PackDB, pack_id)
    if pack_to_delete:
        session.delete(pack_to_delete)
        session.commit()
        return True
    return False