import httpx

CHIMU_URL = "https://catboy.best/"

# status: 1 = ranked
def search_for_beatmaps(keyword: str, status: int=1) -> dict:
    with httpx.Client(base_url=CHIMU_URL) as client:
        response = client.get(f"api/v2/search?q={keyword}&status={status}")
        response.raise_for_status()
        data = response.json()
    
    return data
