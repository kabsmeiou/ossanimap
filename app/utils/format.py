from app.utils.string import replace_spaces_and_dash_with_underscores, remove_special_characters

def format_anime_title_for_animethemes(anime_title: str) -> str:
    """
    Format the anime title to match the expected format for the Animethemes API.
    This includes lowercasing the string and replacing spaces with underscores.
    """
    formatted_title = anime_title.lower()
    formatted_title = replace_spaces_and_dash_with_underscores(formatted_title)
    formatted_title = remove_special_characters(formatted_title)
    return formatted_title