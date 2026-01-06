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
    
# animethemes api expects anime titles to be in lowercase with underscores instead of spaces
def get_anime_metadata(anime_title: str) -> Anime:
    formatted_title = format_anime_title_for_animethemes(anime_title)
    try:
        response = client.get(f"{ANIMETHEMES_URL}anime/{formatted_title}")
    except Exception as e:
        raise Exception(f"Error connecting to animethemes API: {str(e)}")
    
    logger.debug(f"AnimeThemes get_anime_metadata response status: {response.status_code}")
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response for anime '{anime_title}'")
        logger.error(f"Response status: {response.status_code}")
        logger.error(f"Response text (first 500 chars): {response.text[:500]}")
        raise Exception(f"Invalid JSON response from animethemes API: {str(e)}")
    
    anime_metadata = data["anime"] if "anime" in data else {}
    if anime_metadata == {}:
        raise Exception("Anime metadata not found")
    return Anime(**anime_metadata)

def search_anime_by_name(anime_name: str) -> list[AnimeSearchResult]:
    # Ensure URL is clean: https://api.animethemes.moe/search
    url = f"{ANIMETHEMES_URL.rstrip('/')}/search"
    
    params = {
        "q": anime_name, 
        "fields[search]": "anime", 
        "page[limit]": "5"
    }
    
    try:
        response = client.get(url, params=params)
    except Exception as e:
        raise Exception(f"Connection failed: {str(e)}")

    # LOG THE RAW DATA IF IT'S NOT JSON
    content_type = response.headers.get("Content-Type", "")
    
    if "application/json" not in content_type:
        logger.error(f"Unexpected Content-Type: {content_type}")
        logger.error(f"Raw Body: {response.text[:500]}") # This will show the HTML error
        raise Exception(f"Expected JSON but got {content_type}. Check logs for HTML body.")

    try:
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to parse JSON. Text: {response.text[:200]}")
        raise Exception(f"JSON Parsing Error: {str(e)}")

    # Safely navigate the dictionary
    search_data = data.get("search", {})
    anime_list = search_data.get("anime", [])
    
    return [AnimeSearchResult(**anime) for anime in anime_list]