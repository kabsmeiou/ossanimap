import time
import primp
import logging
import json
from app.utils.format import format_anime_title_for_animethemes
from app.utils.parse import extract_anime_data_from_search
from app.schemas.anime import Anime

ANIMETHEMES_URL = "https://api.animethemes.moe/"

logger = logging.getLogger("uvicorn.error")

class AnimeThemesTryLater(Exception):
    """
    Base exception indicating the caller should retry after `retry_after` seconds.
    """

    def __init__(self, retry_after: int = 30):
        self.retry_after = retry_after
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return f"Try again in {self.retry_after} seconds."

    
class AnimeThemesThrottleError(AnimeThemesTryLater):
    def __init__(self, retry_after: int = 30):
        super().__init__(retry_after)

    def __str__(self) -> str:
        return (
            "AnimeThemes API rate limit exceeded. "
            f"Retry after {self.retry_after} seconds."
        )

class AnimeThemesDown(AnimeThemesTryLater):
    """animethemes.moe is unavailable or blocking requests."""

    def __init__(self, status_code: int, retry_after: int = 30):
        self.status_code = status_code
        super().__init__(retry_after)

    def __str__(self) -> str:
        return (
            f"animethemes.moe returned HTTP {self.status_code}. "
            f"Retry after {self.retry_after} seconds."
        )
    
class AnimeThemesRequestError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(self.__str__())
    
    def __str__(self) -> str:
        return f"AnimeThemes API request failed with status code {self.status_code}."

class AnimeThemesInvalidResponse(Exception):
    pass

async def _send_query(url: str, params: dict | None = None) -> dict:
    # check time it takes
    async with primp.AsyncClient(
        impersonate="safari_17.2.1",
        impersonate_os="macos",
        timeout=15,
    ) as client:
        before_request_time = time.perf_counter()
        r = await client.get(url, params=params, timeout=15)
        elapsed = time.perf_counter() - before_request_time
        logger.info("AnimeThemes API request to %s took %.2f seconds", url, elapsed)

    if r.status_code == 429:
        retry_after = int(r.headers.get("Retry-After", 30))
        raise AnimeThemesThrottleError(retry_after)

    if r.status_code >= 500:
        raise AnimeThemesDown(r.status_code)

    if r.status_code != 200:
        raise AnimeThemesRequestError(r.status_code)
    
    raw_text = r.text  # 🔑 force full read ONCE

    try:
        d = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError("Animethemes returned truncated or invalid JSON") from e

    return d

async def fetch_anime_songs_and_alternate_titles(anime_slug: str) -> tuple[list[str], list[str]]:
    params = {
        "include": "animethemes.song,animesynonyms",
    }
    url = f"{ANIMETHEMES_URL.rstrip('/')}/anime/{anime_slug}"
    data = await _send_query(url, params=params)
    anime = data.get("anime", {})
    songs = anime.get("animethemes", [])
    song_titles = [
        s["song"]["title"].lower()
        for s in songs
        if isinstance(s.get("song"), dict) and "title" in s["song"]
    ]
    synonyms = anime.get("animesynonyms", [])
    alt_titles = [
        syn["text"]
        for syn in synonyms
        if "text" in syn and syn["type"] != "Native"
    ]
    return song_titles, alt_titles


async def search_anime_by_name(anime_name: str) -> list[Anime]:
    url = f"{ANIMETHEMES_URL.rstrip('/')}/anime"
    params = {
        "q": anime_name,
        "page[size]": "5",
        "include": "images"
    }
    data = await _send_query(url, params=params)
    # logger.info("Searched anime by name '%s'", data)
    anime_list = extract_anime_data_from_search(data)
    return anime_list


async def check_animethemes_api() -> bool:
    """
    Test connection to AnimeThemes API.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    test_url = f"{ANIMETHEMES_URL.rstrip('/')}/anime"
    try:
        await _send_query(test_url)
        return True
    except Exception as e:
        logger.error(f"AnimeThemes API connection test failed: {str(e)}")
        return False