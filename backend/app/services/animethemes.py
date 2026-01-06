import primp
import logging
from app.utils.format import format_anime_title_for_animethemes
from app.schemas.anime import Anime, AnimeSearchResult

ANIMETHEMES_URL = "https://api.animethemes.moe/"

logger = logging.getLogger("uvicorn.error")

# impersonate with primp
client = primp.Client(
    impersonate="chrome_131",
    impersonate_os="windows"
)
headers = {
    "Referer": "https://animethemes.moe/",
}
client.headers_update(headers)
    
# animethemes api expects anime titles to be in lowercase with underscores instead of spaces
def get_anime_metadata(anime_title: str) -> Anime:
    formatted_title = format_anime_title_for_animethemes(anime_title)
    try:
        response = client.get(f"{ANIMETHEMES_URL}anime/{formatted_title}")
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"Error connecting to animethemes API: {str(e)}")
    data = response.json()
    anime_metadata = data["anime"] if "anime" in data else {}
    if anime_metadata == {}:
        raise Exception("Anime metadata not found")
    return Anime(**anime_metadata)

def search_anime_by_name(anime_name: str) -> list[AnimeSearchResult]:
    try:
        params = {"q": anime_name, "fields[search]": "anime", "page[limit]": 5}
        response = client.get(f"{ANIMETHEMES_URL}search", params=params)
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"Error connecting to animethemes API: {str(e)}")
    # data contains {search: {anime: [...]. animethemes: [...]} }
    data = response.json()
    anime_list = data["search"]["anime"] if "search" in data and "anime" in data["search"] else []
    return [AnimeSearchResult(**anime) for anime in anime_list]