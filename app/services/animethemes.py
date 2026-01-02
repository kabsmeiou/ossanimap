import requests
import json
from app.utils.format import format_anime_title_for_animethemes
from app.models.anime import Anime

ANIMETHEMES_URL = "https://api.animethemes.moe/"

# animethemes api expects anime titles to be in lowercase with underscores instead of spaces
def get_anime_metadata(anime_title: str) -> Anime:
    formatted_title = format_anime_title_for_animethemes(anime_title)
    try:
        response = requests.get(f"{ANIMETHEMES_URL}anime/{formatted_title}")
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Error connecting to animethemes API: {str(e)}")
    data = response.json()
    anime_metadata = data["anime"] if "anime" in data else {}
    if anime_metadata == {}:
        raise Exception("Anime metadata not found")
    return Anime(**anime_metadata)

def search_anime_by_name(anime_name: str) -> list[Anime]:
    try:
        response = requests.get(f"{ANIMETHEMES_URL}search", params={"q": anime_name})
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Error connecting to animethemes API: {str(e)}")
    data = response.json()
    anime_list = data["anime"] if "anime" in data else []
    return [Anime(**anime) for anime in anime_list]