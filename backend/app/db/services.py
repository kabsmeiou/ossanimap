from sqlalchemy import select, func
from .models.anime import AnimeDB
from .models.pack import PackDB
from app.schemas.stats import Stats


async def get_anime_by_id(session, anime_id):
    """Retrieves an Anime by its ID."""
    stmt = select(AnimeDB).where(AnimeDB.id == anime_id)
    result = (await session.scalars(stmt)).first()
    return result

async def save_pack(session, anime_metadata, pack):
    """Saves the Pack and associated Anime to the database."""
    anime_db = await get_anime_by_id(session, anime_metadata.id) if hasattr(anime_metadata, "id") else None
    if not anime_db:
        anime_db = AnimeDB(
            name=anime_metadata.name,
            slug=anime_metadata.slug,
            image_link=anime_metadata.image_link,
        )
        # if anime_metadata provides an ID (from external API), use it so that
        # external references remain stable; otherwise let the DB assign one
        if hasattr(anime_metadata, "id") and anime_metadata.id is not None:
            anime_db.id = anime_metadata.id

        session.add(anime_db)
        await session.flush() 

    pack_db = PackDB(
        name=pack.name,
        anime_id=anime_db.id,
        beatmapset_ids=pack.beatmapset_ids,
        status=pack.status,
        mode=pack.mode,
    )
    session.add(pack_db)
    await session.flush() # flush both anime and pack to assign IDs without committing

    return pack_db

async def list_packs(session):
    """Lists all packs in the database."""
    stmt = select(PackDB)
    result = (await session.scalars(stmt)).all()
    return result

async def get_pack_by_id(session, pack_id):
    """Retrieves a pack by its ID."""
    stmt = select(PackDB).where(PackDB.id == pack_id)
    result = (await session.scalars(stmt)).first()
    return result

async def increment_pack_downloads(session, pack_id):
    """Increments the download count for a specific pack."""
    pack = await get_pack_by_id(session, pack_id)
    pack.downloads += 1
    await session.commit()

async def delete_pack(session, pack_id):
    """
    Deletes a pack by its ID.
    """
    pack_to_delete = await session.get(PackDB, pack_id)
    if pack_to_delete:
        session.delete(pack_to_delete)
        await session.commit()

async def get_global_stats(session) -> Stats:
    total_packs = await session.scalar(
        select(func.count()).select_from(PackDB)
    ) or 0

    total_beatmapsets = await session.scalar(
        select(
            func.sum(
                func.json_array_length(PackDB.beatmapset_ids)
            )
        )
    ) or 0

    total_downloads = await session.scalar(
        select(func.sum(PackDB.downloads))
    ) or 0

    return Stats(
        total_packs=total_packs,
        total_beatmapsets=total_beatmapsets,
        total_downloads=total_downloads,
    )