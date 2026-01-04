from app.services.chimu import search_for_beatmaps, Beatmapset

def test_search_for_beatmaps(mocker):
# Mocked response
    mock_data = [
        {
            "id": 12345,
            "artist": "Some Artist",
            "availability": {"download_disabled": False},
            "beatmaps": [
                {
                    "beatmapset_id": 12345,
                    "difficulty_rating": 5.0,
                    "id": 1,
                    "mode": 0,
                    "mode_int": 0,
                    "status": "ranked",
                    "total_length": 180,
                    "url": "https://catboy.best/b/1"
                },
                {
                    "beatmapset_id": 12345,
                    "difficulty_rating": 4.5,
                    "id": 2,
                    "mode": 0,
                    "mode_int": 0,
                    "status": "ranked",
                    "total_length": 200,
                    "url": "https://catboy.best/b/2"
                }
            ],
            "genre": {"id": 1, "name": "Pop"},
            "nsfw": False,
            "source": "Some Source",
            "status": "ranked",
            "title": "Some Song",
            "title_unicode": "Some Song",
            "track_id": None,
            "ranked": 1
        }
    ]

    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_data
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.Client.get", return_value=mock_response)

    result = search_for_beatmaps("Some Song")

    assert isinstance(result, list)
    assert all(isinstance(r, Beatmapset) for r in result)
    # ensure "ranked" field is not included in output Beatmapset
    for beatmapset in result:
        assert not hasattr(beatmapset, "ranked")
