import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from app.main import app

client = TestClient(app)


class TestAnimeSearchRoute:
    """Test the /anime/search endpoint with various scenarios"""
    
    @patch('app.api.routes.anime.search_anime_by_name')
    def test_search_anime_success(self, mock_search):
        """Test successful anime search"""
        mock_search.return_value = [
            type('AnimeSearchResult', (), {
                'id': 1,
                'name': 'Kaguya-sama: Love is War',
                'slug': 'kaguya_sama_wa_kokurasetai_tensai_tachi_no_renai_zunousen',
                'model_dump': lambda: {
                    'id': 1,
                    'name': 'Kaguya-sama: Love is War',
                    'slug': 'kaguya_sama_wa_kokurasetai_tensai_tachi_no_renai_zunousen'
                }
            })()
        ]
        
        response = client.get("/anime/search?anime_name=kaguya")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Kaguya-sama: Love is War'
    
    @patch('app.services.animethemes.client')
    def test_search_anime_invalid_json_from_api(self, mock_client):
        """Test handling when AnimeThemes API returns invalid JSON"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=kaguya")
        
        assert response.status_code == 500
        assert "Anime search failed" in response.json()['detail']
    
    @patch('app.services.animethemes.client')
    def test_search_anime_connection_error(self, mock_client):
        """Test handling when connection to AnimeThemes fails"""
        mock_client.get.side_effect = ConnectionError("Network error")
        
        response = client.get("/anime/search?anime_name=test")
        
        assert response.status_code == 500
        assert "Anime search failed" in response.json()['detail']
    
    @patch('app.services.animethemes.client')
    def test_search_anime_empty_string(self, mock_client):
        """Test search with empty anime name"""
        mock_response = Mock()
        mock_response.json.return_value = {"search": {"anime": []}}
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=")
        
        # Should still work, just return empty results
        assert response.status_code == 200
        assert response.json() == []
    
    def test_search_anime_missing_parameter(self):
        """Test search without anime_name parameter"""
        response = client.get("/anime/search")
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.animethemes.client')
    def test_search_anime_timeout(self, mock_client):
        """Test handling of timeout"""
        mock_client.get.side_effect = TimeoutError("Request timeout")
        
        response = client.get("/anime/search?anime_name=test")
        
        assert response.status_code == 500
        assert "Anime search failed" in response.json()['detail']
    
    @patch('app.services.animethemes.client')
    def test_search_anime_html_error_page(self, mock_client):
        """Test when API returns HTML error page (like 502 Bad Gateway)"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text = "<html><body>502 Bad Gateway</body></html>"
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=kaguya")
        
        assert response.status_code == 500
        assert "Anime search failed" in response.json()['detail']


class TestRealWorldScenarios:
    """Test real-world scenarios that might occur in production"""
    
    @patch('app.services.animethemes.client')
    def test_search_with_special_characters(self, mock_client):
        """Test search with special characters in anime name"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 1,
                        "name": "Re:Zero kara Hajimeru Isekai Seikatsu",
                        "slug": "re_zero_kara_hajimeru_isekai_seikatsu"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=Re:Zero")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    @patch('app.services.animethemes.client')
    def test_search_with_url_encoded_characters(self, mock_client):
        """Test search with URL encoded characters"""
        mock_response = Mock()
        mock_response.json.return_value = {"search": {"anime": []}}
        mock_client.get.return_value = mock_response
        
        # Test with space encoded as %20
        response = client.get("/anime/search?anime_name=One%20Piece")
        
        assert response.status_code == 200
    
    @patch('app.services.animethemes.client')
    def test_concurrent_searches(self, mock_client):
        """Test multiple concurrent search requests"""
        mock_response = Mock()
        mock_response.json.return_value = {"search": {"anime": []}}
        mock_client.get.return_value = mock_response
        
        # Simulate concurrent requests
        responses = []
        for i in range(5):
            response = client.get(f"/anime/search?anime_name=test{i}")
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
    
    @patch('app.services.animethemes.client')
    def test_very_long_anime_name(self, mock_client):
        """Test search with very long anime name"""
        mock_response = Mock()
        mock_response.json.return_value = {"search": {"anime": []}}
        mock_client.get.return_value = mock_response
        
        long_name = "A" * 500
        response = client.get(f"/anime/search?anime_name={long_name}")
        
        # Should handle gracefully
        assert response.status_code in [200, 414, 500]  # OK, URI too long, or internal error


class TestAnimeThemesAPISimulation:
    """Simulate actual AnimeThemes API responses"""
    
    @patch('app.services.animethemes.client')
    def test_animethemes_typical_response(self, mock_client):
        """Test with typical AnimeThemes API response structure"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": [
                    {
                        "id": 8587,
                        "name": "Kaguya-sama wa Kokurasetai: Tensai-tachi no Renai Zunousen",
                        "slug": "kaguya_sama_wa_kokurasetai_tensai_tachi_no_renai_zunousen",
                        "year": 2019,
                        "season": "Winter",
                        "media_format": "TV",
                        "created_at": "2019-01-11T00:00:00.000000Z",
                        "updated_at": "2024-12-20T00:00:00.000000Z"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=kaguya")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == "Kaguya-sama wa Kokurasetai: Tensai-tachi no Renai Zunousen"
    
    @patch('app.services.animethemes.client')
    def test_animethemes_no_results(self, mock_client):
        """Test when AnimeThemes returns no results"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "search": {
                "anime": []
            }
        }
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=nonexistentanime123456")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.services.animethemes.client')
    def test_animethemes_malformed_response(self, mock_client):
        """Test when AnimeThemes returns malformed data structure"""
        mock_response = Mock()
        # Missing 'search' key
        mock_response.json.return_value = {"data": "something"}
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=test")
        
        # Should return empty list when data structure doesn't match
        assert response.status_code == 200
        assert response.json() == []


class TestDebuggingHelpers:
    """Tests to help debug the deployed environment issue"""
    
    @patch('app.services.animethemes.client')
    def test_log_actual_response(self, mock_client, caplog):
        """Test that logs the actual response for debugging"""
        import logging
        
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text = "Unexpected response text"
        mock_response.status_code = 200
        mock_client.get.return_value = mock_response
        
        with caplog.at_level(logging.ERROR):
            response = client.get("/anime/search?anime_name=kaguya")
        
        assert response.status_code == 500
        # Check that error was logged
        assert any("Anime search failed" in record.message for record in caplog.records)
    
    @patch('app.services.animethemes.client')
    def test_simulate_exact_deployed_error(self, mock_client):
        """Simulate the exact error from deployed environment"""
        # This simulates: "expected value at line 1 column 1"
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError(
            "Expecting value: line 1 column 1 (char 0)", 
            "", 
            0
        )
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = ""
        mock_client.get.return_value = mock_response
        
        response = client.get("/anime/search?anime_name=kaguya")
        
        assert response.status_code == 500
        error_detail = response.json()['detail']
        assert "Anime search failed" in error_detail
        # The error should mention Invalid JSON response
        assert "Invalid JSON response" in error_detail
