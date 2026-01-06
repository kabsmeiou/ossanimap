import primp
import logging
import json
from app.utils.format import format_anime_title_for_animethemes
from app.schemas.anime import Anime, AnimeSearchResult

ANIMETHEMES_URL = "https://api.animethemes.moe/"

logger = logging.getLogger(__name__)

# impersonate with primp
client = primp.Client(
    impersonate="chrome_131",
    impersonate_os="windows"
)
headers = {
    "Referer": "https://api-docs.animethemes.moe/",
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