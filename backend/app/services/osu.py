from ossapi import OssapiAsync
import os
from dotenv import load_dotenv
import logging
import asyncio

from app.utils.format import format_anime_title_for_animethemes
from .animethemes import fetch_anime_songs
from app.schemas.osu import Beatmapset, BeatmapsetSearchMode

load_dotenv()

api = OssapiAsync(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)

logger = logging.getLogger("uvicorn.error")

async def fetch_beatmapset(beatmapset_id: int) -> Beatmapset:
    """
    Fetch beatmapset data from osu! API via Ossapi.

    Args:
        beatmapset_id: The unique beatmapset identifier
    Returns:
        Beatmapset data as a dictionary
    """
    try:
        bm_data = await api.beatmapset(beatmapset_id)
        beatmapset = Beatmapset.model_validate(bm_data, from_attributes=True)
    except Exception as e:
        logger.error(f"Error fetching beatmapset {beatmapset_id}: {str(e)}")
        raise RuntimeError(f"Failed to fetch beatmapset {beatmapset_id}") from e
    logger.info(f"Fetched beatmapset: {beatmapset}")
    return beatmapset


def generate_search_keywords(anime_title: str) -> list[str]:
    keywords = [anime_title]
    special_chars = {":", "-", "–", "|", "/", "\\", ";"}

    running_title = ""
    for i, cur in enumerate(anime_title):
        if cur in special_chars and ((i > 0 and anime_title[i-1] == " ") or (i + 1 < len(anime_title) and anime_title[i+1] == " ")):
            if running_title:
                keywords.append(running_title.strip())
                running_title = ""
        else:
            running_title += cur

    if running_title and running_title.strip() not in keywords:
        keywords.append(running_title.strip())

    final_keywords = keywords
    for kw in keywords:
        cur_kw = kw
        has_changed = False
        for char in special_chars:
            if char in cur_kw:
                cur_kw = cur_kw.replace(char, " ")
                has_changed = True
        if has_changed:
            final_keywords.append(cur_kw.strip())

    return final_keywords


async def search_beatmapsets(keyword: str, source: str | None = None) -> list[Beatmapset]:
    """
    Search for beatmapsets on osu! API via Ossapi.

    Args:
        keyword: Search query (use quotes for exact match)
    Returns:
        List of matching BeatmapsetOSU objects
    """
    try:
        keyword = f'"{keyword}"' if source is None else f'source=""{source}""'
        results = await api.search_beatmapsets(query=keyword, mode=BeatmapsetSearchMode.STANDARD.value)
        # get the beatmapsets from the results, ensure the beatmapset has sources
        beatmapsets: list[Beatmapset] = [
            Beatmapset.model_validate(bm, from_attributes=True)
            for bm in results.beatmapsets
        ]
    except Exception as e:
        logger.error(f"Error searching beatmapsets with keyword '{keyword}': {str(e)}")
        raise Exception(f"Failed to search beatmapsets with keyword '{keyword}'") from e
    return beatmapsets

def check_if_beatmapset_matches_song(bm: Beatmapset, song_list: list[str]) -> bool:
    # remove part with () in osu! title
    beatmap_title = bm.title.lower()
    if "(" in beatmap_title and ")" in beatmap_title:
        beatmap_title = beatmap_title[:beatmap_title.index("(")].strip()
    beatmap_title_unicode = bm.title_unicode.lower() if bm.title_unicode else ""
    return beatmap_title in song_list or beatmap_title_unicode in song_list

async def handle_beatmapset_search(
    anime_title: str,
) -> list[int]:
    """
    Handle beatmapset search using generated keywords.

    Args:
        anime_title: The anime title to search for
    Returns:
        List of unique beatmapset IDs
    """
    formatted_title = format_anime_title_for_animethemes(anime_title)
    song_list = await fetch_anime_songs(formatted_title)
    unique_beatmapsets = set()
    keywords = generate_search_keywords(anime_title)
    sources = set()

    search_calls = [] # create coroutine list for concurrent searching, then await them all at once
    for keyword in keywords:
        search_calls.append(search_beatmapsets(keyword))
    
    beatmapsets_list = await asyncio.gather(*search_calls)
    for beatmapsets in beatmapsets_list:
        for bm in beatmapsets:
            if bm.source and check_if_beatmapset_matches_song(bm, song_list):
                unique_beatmapsets.add(bm.id)
                sources.add(bm.source)

    search_calls = []
    for source in sources:
        search_calls.append(search_beatmapsets(anime_title, source=source))
    
    beatmapsets_list = await asyncio.gather(*search_calls)
    for beatmapsets in beatmapsets_list:
        for bm in beatmapsets:
            if check_if_beatmapset_matches_song(bm, song_list):
                unique_beatmapsets.add(bm.id)
    beatmapset_ids = list(unique_beatmapsets)
    return beatmapset_ids