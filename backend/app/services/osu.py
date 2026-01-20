from ossapi import OssapiAsync
import os
from dotenv import load_dotenv
import logging
import asyncio
import re

from app.utils.format import format_anime_title_for_animethemes
from app.utils.string import normalize_beatmap_title
from .animethemes import fetch_anime_songs_and_alternate_titles
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
    keywords = set()
    keywords.add(anime_title.strip())
    normalized = re.sub(r"[^\w\s]", " ", anime_title)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    keywords.add(normalized)
    return list(keywords)


async def search_beatmapsets(keyword: str | None = None, source: str | None = None) -> list[Beatmapset]:
    """
    Search for beatmapsets on osu! API via Ossapi.

    Args:
        keyword: Search query (use quotes for exact match)
    Returns:
        List of matching BeatmapsetOSU objects
    """
    try:
        keyword = f'"{keyword}"' if source is None else f'source=""{source}""'
        results = await api.search_beatmapsets(query=keyword, mode=BeatmapsetSearchMode.STANDARD.value, category="ranked")
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
    beatmap_title = normalize_beatmap_title(bm.title.lower())
    if "(" in beatmap_title and ")" in beatmap_title:
        beatmap_title = beatmap_title[:beatmap_title.index("(")].strip()
    return beatmap_title in song_list

def collect_all_keywords(anime_title: str, alt_titles: list[str]) -> list[str]:
    titles = [anime_title] + alt_titles
    keywords = []
    seen = set()
    for title in titles:
        for kw in generate_search_keywords(title):
            if kw not in seen:
                keywords.append(kw)
                seen.add(kw)
    return keywords

# so we dont accidentally spam osu! api with bunch of requests at once
# we use semaphore to limit concurrent requests
async def perform_multiple_search_calls(
    keywords: list[str],
    k: int
) -> list[Beatmapset]:
    semaphore = asyncio.Semaphore(k)

    async def limited_search(keyword: str) -> list[Beatmapset]:
        async with semaphore:
            return await search_beatmapsets(keyword)

    search_calls = [limited_search(keyword) for keyword in keywords]
    results = await asyncio.gather(*search_calls)

    # flatten list[list[Beatmapset]] → list[Beatmapset]
    return [bm for batch in results for bm in batch]

async def handle_beatmapset_search(
    anime_title: str,
    anime_slug: str,
) -> list[int]:
    """
    Handle beatmapset search using generated keywords.

    Args:
        anime_title: The anime title to search for
    Returns:
        List of unique beatmapset IDs
    """
    # fetch anime songs from AnimeThemes
    song_list, alt_titles = await fetch_anime_songs_and_alternate_titles(anime_slug)
    song_list = [normalize_beatmap_title(song.lower()) for song in song_list]

    keywords = collect_all_keywords(anime_title, alt_titles)
    
    beatmapsets_list = await perform_multiple_search_calls(keywords, k=5)
    unique_beatmapsets = set()
    sources = {}

    for beatmapsets in beatmapsets_list:
        if beatmapsets.source and check_if_beatmapset_matches_song(beatmapsets, song_list):
            unique_beatmapsets.add(beatmapsets.id)
            # add count of source to dict
            if beatmapsets.source in sources:
                sources[beatmapsets.source] += 1
            else:
                sources[beatmapsets.source] = 1

    sources = dict(sorted(sources.items(), key=lambda item: item[1], reverse=True))
    # search again using sources only, but this is usually just 1-3 extra searches on average
    # you might be wondering why count >= 3? well, if a source appears multiple times, it's more likely to be relevant and its a workaround for beatmaps of cover songs of the anime with a different source.
    sources_list = []
    for source, count in sources.items():
        if count >= 3:
            sources_list.append(source)
    
    beatmapsets_list = await perform_multiple_search_calls(sources_list, k=5)
    for beatmapsets in beatmapsets_list:
            unique_beatmapsets.add(beatmapsets.id)

    beatmapset_ids = list(unique_beatmapsets)
    return beatmapset_ids