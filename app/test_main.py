from fastapi.testclient import TestClient
import logging

from .main import app
client = TestClient(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_search_beatmaps():
    keyword = "\"kaguya-sama: love is war\""
    response = client.get(f"/beatmaps/search/?keyword={keyword}&status=1")
    assert response.status_code == 200
    data = response.json()

    # write data to txt
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write(str(data))