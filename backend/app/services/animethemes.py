import time
import primp
import logging
import json
from app.utils.format import format_anime_title_for_animethemes
from app.schemas.anime import Anime, AnimeSearchResult

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
        raise AnimeThemesDown(r.status_code, retry_after=60)
    
    raw_text = r.text  # 🔑 force full read ONCE

    try:
        d = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise AnimeThemesInvalidResponse("Animethemes returned truncated or invalid JSON") from e

    return d
    
# animethemes api expects anime titles to be in lowercase with underscores instead of spaces
async def get_anime_metadata(anime_title: str) -> Anime:
    formatted_title = format_anime_title_for_animethemes(anime_title)
    url = f"{ANIMETHEMES_URL.rstrip('/')}/anime/{formatted_title}"
    data = await _send_query(url)
    anime_metadata = data["anime"] if "anime" in data else {}
    return Anime(**anime_metadata)


async def search_anime_by_name(anime_name: str) -> list[AnimeSearchResult]:
    url = f"{ANIMETHEMES_URL.rstrip('/')}/anime"
    params = {
        "q": anime_name,
        "page[size]": "5",
    }
    logger.info("url: %s, params: %s", url, params)
    data = await _send_query(url, params=params)
    anime_list = data.get("anime", [])
    return [AnimeSearchResult(**anime) for anime in anime_list]
