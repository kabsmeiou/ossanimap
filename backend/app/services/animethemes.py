import primp
import logging
import json
from app.utils.format import format_anime_title_for_animethemes
from app.schemas.anime import Anime, AnimeSearchResult

ANIMETHEMES_URL = "https://api.animethemes.moe/"

logger = logging.getLogger(__name__)

# impersonate with primp
client = primp.Client(
    impersonate="safari_17.2.1",
    impersonate_os="macos"
)
# These headers are what modern Chrome sends to prove it's a real browser
headers = {
    "Authority": "api.animethemes.moe",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://animethemes.moe/",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
client.headers_update(headers)

def _send_query(url: str, params: dict | None = None) -> dict:
    try:
        r = client.get(url, params=params, timeout=15)
    except Exception as e:
        raise Exception(f"Connection failed: {str(e)}")

    raw_text = r.text  # 🔑 force full read ONCE
    logger.debug(
        f"AnimeThemes response "
        f"(status={r.status_code}, len={len(raw_text)})"
    )

    if r.status_code != 200:
        logger.error(f"Non-200 response: {raw_text[:300]}")
        raise Exception(f"Animethemes API error {r.status_code}")

    try:
        d = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error("JSON parse failed")
        logger.error(f"Last 300 chars:\n{raw_text[-300:]}")
        raise Exception("Animethemes returned truncated or invalid JSON")

    return d
    
# animethemes api expects anime titles to be in lowercase with underscores instead of spaces
def get_anime_metadata(anime_title: str) -> Anime:
    formatted_title = format_anime_title_for_animethemes(anime_title)
    url = f"{ANIMETHEMES_URL.rstrip('/')}/anime/{formatted_title}"
    data = _send_query(url)
    anime_metadata = data["anime"] if "anime" in data else {}
    if anime_metadata == {}:
        raise Exception("Anime metadata not found")
    return Anime(**anime_metadata)


def search_anime_by_name(anime_name: str) -> list[AnimeSearchResult]:
    url = f"{ANIMETHEMES_URL.rstrip('/')}/search"
    params = {
        "q": anime_name,
        "fields[search]": "anime",
        "page[limit]": 5,
    }
    data = _send_query(url, params=params)
    anime_list = data.get("search", {}).get("anime", [])
    return [AnimeSearchResult(**anime) for anime in anime_list]
