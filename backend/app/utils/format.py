from pydantic import ValidationError

from app.utils.string import replace_spaces_and_dash_with_underscores, remove_special_characters
from app.schemas.pack import Pack
from app.db.models.pack import PackDB


def format_anime_title_for_animethemes(anime_title: str) -> str:
    """
    Format the anime title to match the expected format for the Animethemes API.
    This includes lowercasing the string and replacing spaces with underscores.
    """
    formatted_title = anime_title.lower()
    formatted_title = replace_spaces_and_dash_with_underscores(formatted_title)
    formatted_title = remove_special_characters(formatted_title)
    return formatted_title

def packdb_to_packschema(pack_db: PackDB) -> Pack:
    """
    Convert a Pack database model instance to a Pack schema dictionary. used for DB objects to API responses.
    """
    try:
        # load anime metadata from anime_id foreign key
        pack = Pack(
            id=pack_db.id,
            name=pack_db.name,
            anime_title=pack_db.anime.name,
            anime_slug=pack_db.anime.slug,
            synopsis=pack_db.anime.synopsis,
            beatmapset_ids=pack_db.beatmapset_ids,
            downloads=pack_db.downloads,
            created_at=pack_db.created_at.isoformat() if pack_db.created_at is not None else None,
            beatmapset_count=pack_db.beatmapset_count,
            updated_at=pack_db.updated_at.isoformat() if pack_db.updated_at is not None else None,
        )
        return pack
    except ValidationError as e:
        raise f"Failed to convert PackDB to Pack schema: {str(e)}"