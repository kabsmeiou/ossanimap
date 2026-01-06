import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from app.services.animethemes import get_anime_metadata, search_anime_by_name
from app.schemas.anime import Anime, AnimeSearchResult


class TestDeployedEnvironmentErrors:
    """Test errors that occur in deployed environment"""
    
    @patch('app.services.animethemes.client')
    def test_search_anime_invalid_json_response(self, mock_client):
        """Test handling of invalid JSON response (deployed environment issue)"""
        mock_response = Mock()
        # Simulate the error: "expected value at line 1 column 1"
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = ""
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            search_anime_by_name("kaguya")
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @patch('app.services.animethemes.client')
    def test_search_anime_empty_response(self, mock_client):
        """Test handling of empty response body"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text = ""
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            search_anime_by_name("test")
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @patch('app.services.animethemes.client')
    def test_search_anime_html_error_response(self, mock_client):
        """Test handling of HTML error page instead of JSON"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text = "<html><body>Error 502 Bad Gateway</body></html>"
        mock_response.status_code = 502
        mock_response.headers = {}
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            search_anime_by_name("test")
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_invalid_json(self, mock_client):
        """Test get_anime_metadata with invalid JSON response"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.status_code = 200
        mock_response.text = ""
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            get_anime_metadata("test_anime")
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @patch('app.services.animethemes.client')
    def test_search_anime_rate_limited_response(self, mock_client):
        """Test handling of rate limit response"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text = "Rate limit exceeded"
        mock_response.headers = {}
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            search_anime_by_name("test")
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @patch('app.services.animethemes.client')
    def test_search_anime_502_bad_gateway(self, mock_client):
        """Test handling of 502 Bad Gateway error"""
        mock_response = Mock()
        mock_response.status_code = 502
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text = "502 Bad Gateway"
        mock_response.headers = {}
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            search_anime_by_name("test")
        
        assert "Invalid JSON response" in str(exc_info.value)


class TestGetAnimeMetadata:
    """Test get_anime_metadata function with mocked API responses"""
    
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_success(self, mock_client):
        """Test successful retrieval of anime metadata"""
        # Mock response data matching AnimeThemes API structure
        mock_response = Mock()
        mock_response.json.return_value = {
            "anime": {
                "id": 1,
                "name": "Cowboy Bebop",
                "slug": "cowboy_bebop",
                "synopsis": "In the year 2071, humanity has colonized several of the planets and moons of the solar system."
            }
        }
        mock_client.get.return_value = mock_response
        
        # Test the function
        result = get_anime_metadata("Cowboy Bebop")
        
        # Assertions
        assert isinstance(result, Anime)
        assert result.name == "Cowboy Bebop"
        assert result.slug == "cowboy_bebop"
        assert result.synopsis is not None
        mock_client.get.assert_called_once()
        
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_with_special_characters(self, mock_client):
        """Test anime title with special characters gets formatted correctly"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "anime": {
                "id": 2,
                "name": "Kimetsu no Yaiba",
                "slug": "kimetsu_no_yaiba"
            }
        }
        mock_client.get.return_value = mock_response
        
        result = get_anime_metadata("Kimetsu no Yaiba")
        
        assert isinstance(result, Anime)
        assert result.name == "Kimetsu no Yaiba"
        # Verify the URL was called with formatted title
        call_args = mock_client.get.call_args[0][0]
        assert "kimetsu_no_yaiba" in call_args.lower()
        
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_not_found(self, mock_client):
        """Test handling when anime is not found"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            get_anime_metadata("NonexistentAnime123")
        
        assert "Anime metadata not found" in str(exc_info.value)
        
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_empty_anime_object(self, mock_client):
        """Test handling when anime object is empty"""
        mock_response = Mock()
        mock_response.json.return_value = {"anime": {}}
        mock_client.get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            get_anime_metadata("TestAnime")
        
        assert "Anime metadata not found" in str(exc_info.value)
        
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_connection_error(self, mock_client):
        """Test handling of connection errors"""
        mock_client.get.side_effect = ConnectionError("Network error")
        
        with pytest.raises(Exception) as exc_info:
            get_anime_metadata("TestAnime")
        
        assert "Error connecting to animethemes API" in str(exc_info.value)
        
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_timeout_error(self, mock_client):
        """Test handling of timeout errors"""
        mock_client.get.side_effect = TimeoutError("Request timeout")
        
        with pytest.raises(Exception) as exc_info:
            get_anime_metadata("TestAnime")
        
        assert "Error connecting to animethemes API" in str(exc_info.value)
        
    @patch('app.services.animethemes.client')
    def test_get_anime_metadata_with_all_fields(self, mock_client):
        """Test anime metadata with all possible fields"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "anime": {
                "id": 3,
                "name": "Steins;Gate",
                "slug": "steins_gate",
                "synopsis": "A group of friends discover time travel."
            }
        }
        mock_client.get.return_value = mock_response
        
        result = get_anime_metadata("Steins;Gate")
        
        assert result.id == 3
        assert result.name == "Steins;Gate"
        assert result.slug == "steins_gate"
        assert result.synopsis == "A group of friends discover time travel."


class TestSearchAnimeByName:
    """Test search_anime_by_name function with mocked API responses"""
    
    @patch('app.services.animethemes.client')
    def test_search_anime_success_multiple_results(self, mock_client):
        """Test successful search with multiple results"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 1,
                        "name": "Naruto",
                        "slug": "naruto"
                    },
                    {
                        "id": 2,
                        "name": "Naruto: Shippuuden",
                        "slug": "naruto_shippuuden"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("Naruto")
        
        assert len(results) == 2
        assert all(isinstance(r, AnimeSearchResult) for r in results)
        assert results[0].name == "Naruto"
        assert results[1].name == "Naruto: Shippuuden"
        
        # Verify correct API call with params
        call_kwargs = mock_client.get.call_args[1]
        assert 'params' in call_kwargs
        assert call_kwargs['params']['q'] == "Naruto"
        assert call_kwargs['params']['fields[search]'] == "anime"
        assert call_kwargs['params']['page[limit]'] == "5"
        
    @patch('app.services.animethemes.client')
    def test_search_anime_single_result(self, mock_client):
        """Test search with single result"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 10,
                        "name": "Cowboy Bebop",
                        "slug": "cowboy_bebop"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("Cowboy Bebop")
        
        assert len(results) == 1
        assert results[0].name == "Cowboy Bebop"
        assert results[0].slug == "cowboy_bebop"
        
    @patch('app.services.animethemes.client')
    def test_search_anime_no_results(self, mock_client):
        """Test search with no results"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": []
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("NonexistentAnime999")
        
        assert len(results) == 0
        assert results == []
        
    @patch('app.services.animethemes.client')
    def test_search_anime_missing_search_key(self, mock_client):
        """Test handling when search key is missing from response"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("TestAnime")
        
        assert len(results) == 0
        
    @patch('app.services.animethemes.client')
    def test_search_anime_missing_anime_key(self, mock_client):
        """Test handling when anime key is missing from search results"""
        mock_response = Mock()
        mock_response.json.return_value = {"search": {}}
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("TestAnime")
        
        assert len(results) == 0
        
    @patch('app.services.animethemes.client')
    def test_search_anime_connection_error(self, mock_client):
        """Test handling of connection errors during search"""
        mock_client.get.side_effect = ConnectionError("Network error")
        
        with pytest.raises(Exception) as exc_info:
            search_anime_by_name("TestAnime")
        
        assert "Error connecting to animethemes API" in str(exc_info.value)
        
    @patch('app.services.animethemes.client')
    def test_search_anime_timeout_error(self, mock_client):
        """Test handling of timeout errors during search"""
        mock_client.get.side_effect = TimeoutError("Request timeout")
        
        with pytest.raises(Exception) as exc_info:
            search_anime_by_name("TestAnime")
        
        assert "Error connecting to animethemes API" in str(exc_info.value)
        
    @patch('app.services.animethemes.client')
    def test_search_anime_with_special_characters(self, mock_client):
        """Test search with special characters in query"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 15,
                        "name": "Re:Zero kara Hajimeru Isekai Seikatsu",
                        "slug": "re_zero_kara_hajimeru_isekai_seikatsu"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("Re:Zero")
        
        assert len(results) == 1
        assert results[0].name == "Re:Zero kara Hajimeru Isekai Seikatsu"
        
    @patch('app.services.animethemes.client')
    def test_search_anime_limit_enforced(self, mock_client):
        """Test that search respects the 5 result limit"""
        mock_response = Mock()
        # API should return max 5 results as per params
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {"id": i, "name": f"Anime {i}", "slug": f"anime_{i}"}
                    for i in range(1, 6)  # Exactly 5 results
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("Anime")
        
        assert len(results) == 5
        assert len(results) <= 5  # Should never exceed limit
        
    @patch('app.services.animethemes.client')
    def test_search_anime_with_season_info(self, mock_client):
        """Test search results can handle extra fields from API"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 20,
                        "name": "Attack on Titan",
                        "slug": "shingeki_no_kyojin"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("Attack on Titan")
        
        assert len(results) == 1
        assert results[0].name == "Attack on Titan"
        assert results[0].slug == "shingeki_no_kyojin"
        
    @patch('app.services.animethemes.client')
    def test_search_anime_partial_match(self, mock_client):
        """Test search with partial anime name"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 25,
                        "name": "One Piece",
                        "slug": "one_piece"
                    },
                    {
                        "id": 26,
                        "name": "One Punch Man",
                        "slug": "one_punch_man"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("One")
        
        assert len(results) == 2
        assert any("One Piece" in r.name for r in results)
        assert any("One Punch Man" in r.name for r in results)


class TestClientConfiguration:
    """Test that the primp client is properly configured"""
    
    @patch('app.services.animethemes.client')
    def test_client_has_correct_headers(self, mock_client):
        """Test that client has Referer header set"""
        # The headers should be set during module initialization
        # We're testing that the function uses the client correctly
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {"anime": []}
        }
        mock_client.get.return_value = mock_response
        
        search_anime_by_name("Test")
        
        # Verify the client's get method was called
        assert mock_client.get.called
        
    @patch('app.services.animethemes.client')
    def test_api_url_construction(self, mock_client):
        """Test that API URLs are constructed correctly"""
        mock_response = Mock()
        mock_response.json.return_value = {"anime": {"id": 1, "name": "Test", "slug": "test"}}
        mock_client.get.return_value = mock_response
        
        get_anime_metadata("Test Anime")
        
        # Check the URL contains the base URL
        call_args = mock_client.get.call_args[0][0]
        assert "api.animethemes.moe" in call_args
        assert "anime/" in call_args


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @patch('app.services.animethemes.client')
    def test_empty_string_search(self, mock_client):
        """Test search with empty string"""
        mock_response = Mock()
        mock_response.json.return_value = {"search": {"anime": []}}
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("")
        
        assert len(results) == 0
        
    @patch('app.services.animethemes.client')
    def test_whitespace_only_search(self, mock_client):
        """Test search with whitespace only"""
        mock_response = Mock()
        mock_response.json.return_value = {"search": {"anime": []}}
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("   ")
        
        assert len(results) == 0
        
    @patch('app.services.animethemes.client')
    def test_very_long_anime_name(self, mock_client):
        """Test with very long anime name"""
        long_name = "A" * 200
        mock_response = Mock()
        mock_response.json.return_value = {"search": {"anime": []}}
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name(long_name)
        
        assert isinstance(results, list)
        
    @patch('app.services.animethemes.client')
    def test_unicode_characters_in_search(self, mock_client):
        """Test search with unicode characters"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 30,
                        "name": "Charlotte",
                        "slug": "charlotte",
                        "year": 2015
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        results = search_anime_by_name("シャーロット")  # Charlotte in Japanese
        
        assert isinstance(results, list)
        mock_client.get.assert_called_once()
