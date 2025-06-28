import pytest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch service dependencies before importing function modules
patch_db = patch('services.database.DatabaseService')
patch_auth = patch('services.auth.AuthService')
patch_user = patch('services.user_service.UserService')
MockDatabaseService = patch_db.start()
MockAuthService = patch_auth.start()
MockUserService = patch_user.start()

# Set up return values for the mocks
mock_db_service = MagicMock()
mock_auth_service = MagicMock()
mock_user_service = MagicMock()
MockDatabaseService.return_value = mock_db_service
MockAuthService.return_value = mock_auth_service
MockUserService.return_value = mock_user_service

# Import the function modules
import health
import auth
import users
import dungeons
import guilds
import lobbies
import friends
import leaderboard

# Stop patchers after import
patch_db.stop()
patch_auth.stop()
patch_user.stop()

def make_mock_request(body=None, headers=None, method="POST", route_params=None):
    """Create a mock HttpRequest object"""
    mock_request = MagicMock()
    mock_request.method = method
    mock_request.headers = headers or {}
    mock_request.route_params = route_params or {}
    
    if body:
        mock_request.get_json.return_value = body
    else:
        mock_request.get_json.return_value = {}
    
    return mock_request

class TestHealthFunction:
    def test_health_check_success(self):
        """Test successful health check."""
        mock_request = make_mock_request(method="GET")
        with patch('health.func.HttpResponse') as MockHttpResponse:
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = health._health_check_impl(mock_request)
            assert response is mock_response

class TestAuthEndpoints:
    def test_register_success(self):
        mock_request = make_mock_request({
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "display_name": "Test User"
        })
        with patch.object(auth, 'user_service') as mock_user_service, \
             patch.object(auth, 'auth_service') as mock_auth_service, \
             patch('auth.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_user.username = "testuser"
            mock_user.email = "test@example.com"
            mock_user.display_name = "Test User"
            mock_user_service.create_user.return_value = mock_user
            mock_auth_service.create_access_token.return_value = "mock-token"
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = auth._register_impl(mock_request)
            assert response is mock_response

    def test_login_success(self):
        mock_request = make_mock_request({
            "username": "testuser",
            "password": "password123"
        })
        with patch.object(auth, 'auth_service') as mock_auth_service, \
             patch.object(auth, 'user_service') as mock_user_service, \
             patch('auth.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_user.username = "testuser"
            mock_user.email = "test@example.com"
            mock_user.display_name = "Test User"
            mock_auth_service.authenticate_user.return_value = mock_user
            mock_user_service.update_last_login.return_value = True
            mock_auth_service.create_access_token.return_value = "mock-token"
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = auth._login_impl(mock_request)
            assert response is mock_response

    def test_get_current_user_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(auth, 'auth_service') as mock_auth_service, \
             patch.object(auth, 'user_service') as mock_user_service, \
             patch('auth.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_profile = MagicMock()
            mock_profile.dict.return_value = {
                "id": "user-123",
                "username": "testuser",
                "level": 1,
                "experience": 0
            }
            mock_user_service.get_user_profile.return_value = mock_profile
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = auth._get_current_user_impl(mock_request)
            assert response is mock_response

class TestUserEndpoints:
    def test_get_user_profile_success(self):
        mock_request = make_mock_request(method="GET", route_params={"user_id": "user-123"})
        with patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_profile = MagicMock()
            mock_profile.dict.return_value = {"id": "user-123"}
            mock_user_service.get_user_profile.return_value = mock_profile
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_user_profile_impl(mock_request)
            assert response is mock_response

    def test_get_user_profile_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"user_id": "user-123"})
        with patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user_service.get_user_profile.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_user_profile_impl(mock_request)
            assert response is mock_response

    def test_get_users_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"search": "test", "limit": "10"}
        with patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.dict.return_value = {"id": "user-123"}
            mock_user_service.search_users.return_value = [mock_user]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_users_impl(mock_request)
            assert response is mock_response

    def test_get_users_missing_search(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch('users.func.HttpResponse') as MockHttpResponse:
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_users_impl(mock_request)
            assert response is mock_response

    def test_get_users_internal_error(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"search": "test", "limit": "10"}
        with patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user_service.search_users.side_effect = Exception("fail")
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_users_impl(mock_request)
            assert response is mock_response

    def test_update_profile_success(self):
        mock_request = make_mock_request({
            "display_name": "New Name",
            "avatar_url": "https://example.com/avatar.jpg"
        }, headers={"Authorization": "Bearer mock-token"}, method="PUT")
        with patch.object(users, 'auth_service') as mock_auth_service, \
             patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_updated_user = MagicMock()
            mock_updated_user.dict.return_value = {"id": "user-123", "display_name": "New Name"}
            mock_user_service.update_user_profile.return_value = mock_updated_user
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._update_profile_impl(mock_request)
            assert response is mock_response

    def test_update_profile_unauthorized(self):
        mock_request = make_mock_request({
            "display_name": "New Name"
        }, headers={}, method="PUT")
        with patch.object(users, 'auth_service') as mock_auth_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._update_profile_impl(mock_request)
            assert response is mock_response

    def test_update_profile_no_valid_fields(self):
        mock_request = make_mock_request({
            "invalid_field": "value"
        }, headers={"Authorization": "Bearer mock-token"}, method="PUT")
        with patch.object(users, 'auth_service') as mock_auth_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._update_profile_impl(mock_request)
            assert response is mock_response

    def test_update_profile_service_failure(self):
        mock_request = make_mock_request({
            "display_name": "New Name"
        }, headers={"Authorization": "Bearer mock-token"}, method="PUT")
        with patch.object(users, 'auth_service') as mock_auth_service, \
             patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_user_service.update_user_profile.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._update_profile_impl(mock_request)
            assert response is mock_response

    def test_get_my_profile_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(users, 'auth_service') as mock_auth_service, \
             patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_profile = MagicMock()
            mock_profile.dict.return_value = {"id": "user-123"}
            mock_user_service.get_user_profile.return_value = mock_profile
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_my_profile_impl(mock_request)
            assert response is mock_response

    def test_get_my_profile_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="GET")
        with patch.object(users, 'auth_service') as mock_auth_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_my_profile_impl(mock_request)
            assert response is mock_response

    def test_get_my_profile_not_found(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(users, 'auth_service') as mock_auth_service, \
             patch.object(users, 'user_service') as mock_user_service, \
             patch('users.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_user_service.get_user_profile.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = users._get_my_profile_impl(mock_request)
            assert response is mock_response

class TestDungeonEndpoints:
    def test_create_dungeon_success(self):
        mock_request = make_mock_request({
            "name": "Test Dungeon",
            "description": "A test dungeon",
            "difficulty": "medium",
            "dungeon_data": {"rooms": [], "monsters": [], "traps": [], "treasures": []},
            "tags": ["test"],
            "is_public": True
        }, headers={"Authorization": "Bearer mock-token"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_dungeon = MagicMock()
            mock_dungeon.id = "dungeon-123"
            mock_dungeon.name = "Test Dungeon"
            mock_dungeon.creator_id = "user-123"
            mock_dungeon_service.create_dungeon.return_value = mock_dungeon
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._create_dungeon_impl(mock_request)
            assert response is mock_response

    def test_get_dungeons_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10", "offset": "0"}
        with patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_dungeon = MagicMock()
            mock_dungeon.dict.return_value = {"id": "dungeon-123"}
            mock_dungeon_service.get_public_dungeons.return_value = [mock_dungeon]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._get_dungeons_impl(mock_request)
            assert response is mock_response

    def test_get_dungeons_internal_error(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10", "offset": "0"}
        with patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_dungeon_service.get_public_dungeons.side_effect = Exception("fail")
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._get_dungeons_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_success(self):
        mock_request = make_mock_request(method="GET", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_dungeon = MagicMock()
            mock_dungeon.dict.return_value = {"id": "dungeon-123"}
            mock_dungeon_service.get_dungeon_by_id.return_value = mock_dungeon
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._get_dungeon_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_dungeon_service.get_dungeon_by_id.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._get_dungeon_impl(mock_request)
            assert response is mock_response

    def test_update_dungeon_success(self):
        mock_request = make_mock_request({"name": "Updated"}, headers={"Authorization": "Bearer mock-token"}, method="PUT", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_dungeon = MagicMock()
            mock_dungeon.dict.return_value = {"id": "dungeon-123"}
            mock_dungeon_service.update_dungeon.return_value = mock_dungeon
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._update_dungeon_impl(mock_request)
            assert response is mock_response

    def test_update_dungeon_unauthorized(self):
        mock_request = make_mock_request({"name": "Updated"}, headers={}, method="PUT", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._update_dungeon_impl(mock_request)
            assert response is mock_response

    def test_update_dungeon_not_found(self):
        mock_request = make_mock_request({"name": "Updated"}, headers={"Authorization": "Bearer mock-token"}, method="PUT", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_dungeon_service.update_dungeon.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._update_dungeon_impl(mock_request)
            assert response is mock_response

    def test_delete_dungeon_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="DELETE", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_dungeon_service.delete_dungeon.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._delete_dungeon_impl(mock_request)
            assert response is mock_response

    def test_delete_dungeon_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="DELETE", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._delete_dungeon_impl(mock_request)
            assert response is mock_response

    def test_delete_dungeon_not_found(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="DELETE", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_dungeon_service.delete_dungeon.return_value = False
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._delete_dungeon_impl(mock_request)
            assert response is mock_response

    def test_rate_dungeon_success(self):
        mock_request = make_mock_request({"rating": 5, "comment": "Great!"}, headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_rating = MagicMock()
            mock_rating.dict.return_value = {"id": "rating-123"}
            mock_dungeon_service.rate_dungeon.return_value = mock_rating
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._rate_dungeon_impl(mock_request)
            assert response is mock_response

    def test_rate_dungeon_unauthorized(self):
        mock_request = make_mock_request({"rating": 5, "comment": "Great!"}, headers={}, method="POST", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._rate_dungeon_impl(mock_request)
            assert response is mock_response

    def test_rate_dungeon_invalid_rating(self):
        mock_request = make_mock_request({"rating": 10, "comment": "Bad!"}, headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'auth_service') as mock_auth_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._rate_dungeon_impl(mock_request)
            assert response is mock_response

    def test_play_dungeon_success(self):
        mock_request = make_mock_request(method="POST", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_dungeon_service.increment_play_count.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._play_dungeon_impl(mock_request)
            assert response is mock_response

    def test_play_dungeon_internal_error(self):
        mock_request = make_mock_request(method="POST", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(dungeons, 'dungeon_service') as mock_dungeon_service, \
             patch('dungeons.func.HttpResponse') as MockHttpResponse:
            mock_dungeon_service.increment_play_count.side_effect = Exception("fail")
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = dungeons._play_dungeon_impl(mock_request)
            assert response is mock_response

class TestGuildEndpoints:
    def test_create_guild_success(self):
        mock_request = make_mock_request({
            "name": "Test Guild",
            "description": "A test guild",
            "max_members": 50,
            "is_public": True
        }, headers={"Authorization": "Bearer mock-token"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_guild = MagicMock()
            mock_guild.id = "guild-123"
            mock_guild.name = "Test Guild"
            mock_guild.leader_id = "user-123"
            mock_guild_service.create_guild.return_value = mock_guild
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._create_guild_impl(mock_request)
            assert response is mock_response

    def test_get_guilds_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_guild = MagicMock()
            mock_guild.dict.return_value = {"id": "guild-123"}
            mock_guild_service.get_public_guilds.return_value = [mock_guild]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_guilds_impl(mock_request)
            assert response is mock_response

    def test_get_guilds_internal_error(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_guild_service.get_public_guilds.side_effect = Exception("fail")
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_guilds_impl(mock_request)
            assert response is mock_response

    def test_get_guild_success(self):
        mock_request = make_mock_request(method="GET", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_guild = MagicMock()
            mock_guild.dict.return_value = {"id": "guild-123"}
            mock_guild_service.get_guild_by_id.return_value = mock_guild
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_guild_impl(mock_request)
            assert response is mock_response

    def test_get_guild_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_guild_service.get_guild_by_id.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_guild_impl(mock_request)
            assert response is mock_response

    def test_get_guild_members_success(self):
        mock_request = make_mock_request(method="GET", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_member = MagicMock()
            mock_member.dict.return_value = {"id": "user-123"}
            mock_guild_service.get_guild_members.return_value = [mock_member]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_guild_members_impl(mock_request)
            assert response is mock_response

    def test_add_guild_member_success(self):
        mock_request = make_mock_request({"user_id": "user-456", "role": "member"}, headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_guild_service.add_member_to_guild.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._add_guild_member_impl(mock_request)
            assert response is mock_response

    def test_add_guild_member_unauthorized(self):
        mock_request = make_mock_request({"user_id": "user-456"}, headers={}, method="POST", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._add_guild_member_impl(mock_request)
            assert response is mock_response

    def test_add_guild_member_missing_user_id(self):
        mock_request = make_mock_request({}, headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._add_guild_member_impl(mock_request)
            assert response is mock_response

    def test_remove_guild_member_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="DELETE", route_params={"guild_id": "guild-123", "member_id": "user-456"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_guild_service.remove_member_from_guild.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._remove_guild_member_impl(mock_request)
            assert response is mock_response

    def test_remove_guild_member_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="DELETE", route_params={"guild_id": "guild-123", "member_id": "user-456"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._remove_guild_member_impl(mock_request)
            assert response is mock_response

    def test_update_guild_success(self):
        mock_request = make_mock_request({"name": "Updated Guild"}, headers={"Authorization": "Bearer mock-token"}, method="PUT", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_guild = MagicMock()
            mock_guild.dict.return_value = {"id": "guild-123"}
            mock_guild_service.update_guild.return_value = mock_guild
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._update_guild_impl(mock_request)
            assert response is mock_response

    def test_update_guild_unauthorized(self):
        mock_request = make_mock_request({"name": "Updated Guild"}, headers={}, method="PUT", route_params={"guild_id": "guild-123"})
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._update_guild_impl(mock_request)
            assert response is mock_response

    def test_get_my_guild_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_guild = MagicMock()
            mock_guild.dict.return_value = {"id": "guild-123"}
            mock_guild_service.get_user_guild.return_value = mock_guild
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_my_guild_impl(mock_request)
            assert response is mock_response

    def test_get_my_guild_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="GET")
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_my_guild_impl(mock_request)
            assert response is mock_response

    def test_get_my_guild_not_found(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(guilds, 'auth_service') as mock_auth_service, \
             patch.object(guilds, 'guild_service') as mock_guild_service, \
             patch('guilds.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_guild_service.get_user_guild.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = guilds._get_my_guild_impl(mock_request)
            assert response is mock_response

class TestLobbyEndpoints:
    def test_create_lobby_success(self):
        mock_request = make_mock_request({
            "name": "Test Lobby",
            "description": "A test lobby",
            "max_players": 4,
            "is_public": True
        }, headers={"Authorization": "Bearer mock-token"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby = MagicMock()
            mock_lobby.id = "lobby-123"
            mock_lobby.name = "Test Lobby"
            mock_lobby.creator_id = "user-123"
            mock_lobby_service.create_lobby.return_value = mock_lobby
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._create_lobby_impl(mock_request)
            assert response is mock_response

    def test_get_lobbies_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_lobby = MagicMock()
            mock_lobby.dict.return_value = {"id": "lobby-123"}
            mock_lobby_service.get_public_lobbies.return_value = [mock_lobby]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._get_lobbies_impl(mock_request)
            assert response is mock_response

    def test_get_lobbies_internal_error(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_lobby_service.get_public_lobbies.side_effect = Exception("fail")
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._get_lobbies_impl(mock_request)
            assert response is mock_response

    def test_get_lobby_success(self):
        mock_request = make_mock_request(method="GET", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_lobby = MagicMock()
            mock_lobby.dict.return_value = {"id": "lobby-123"}
            mock_lobby_service.get_lobby_by_id.return_value = mock_lobby
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._get_lobby_impl(mock_request)
            assert response is mock_response

    def test_get_lobby_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_lobby_service.get_lobby_by_id.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._get_lobby_impl(mock_request)
            assert response is mock_response

    def test_join_lobby_success(self):
        mock_request = make_mock_request({"password": "secret"}, headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby_service.join_lobby.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._join_lobby_impl(mock_request)
            assert response is mock_response

    def test_join_lobby_unauthorized(self):
        mock_request = make_mock_request({"password": "secret"}, headers={}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._join_lobby_impl(mock_request)
            assert response is mock_response

    def test_leave_lobby_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby_service.leave_lobby.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._leave_lobby_impl(mock_request)
            assert response is mock_response

    def test_leave_lobby_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._leave_lobby_impl(mock_request)
            assert response is mock_response

    def test_start_lobby_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby_service.start_lobby.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._start_lobby_impl(mock_request)
            assert response is mock_response

    def test_start_lobby_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._start_lobby_impl(mock_request)
            assert response is mock_response

    def test_complete_lobby_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby_service.complete_lobby.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._complete_lobby_impl(mock_request)
            assert response is mock_response

    def test_cancel_lobby_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby_service.cancel_lobby.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._cancel_lobby_impl(mock_request)
            assert response is mock_response

    def test_invite_to_lobby_success(self):
        mock_request = make_mock_request({"user_id": "user-456"}, headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_invite = MagicMock()
            mock_invite.dict.return_value = {"id": "invite-123"}
            mock_lobby_service.create_lobby_invite.return_value = mock_invite
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._invite_to_lobby_impl(mock_request)
            assert response is mock_response

    def test_invite_to_lobby_unauthorized(self):
        mock_request = make_mock_request({"user_id": "user-456"}, headers={}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._invite_to_lobby_impl(mock_request)
            assert response is mock_response

    def test_invite_to_lobby_missing_user_id(self):
        mock_request = make_mock_request({}, headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"lobby_id": "lobby-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._invite_to_lobby_impl(mock_request)
            assert response is mock_response

    def test_get_lobby_invites_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_invite = MagicMock()
            mock_invite.dict.return_value = {"id": "invite-123"}
            mock_lobby_service.get_lobby_invites.return_value = [mock_invite]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._get_lobby_invites_impl(mock_request)
            assert response is mock_response

    def test_get_lobby_invites_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="GET")
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._get_lobby_invites_impl(mock_request)
            assert response is mock_response

    def test_accept_lobby_invite_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"invite_id": "invite-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby_service.accept_lobby_invite.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._accept_lobby_invite_impl(mock_request)
            assert response is mock_response

    def test_accept_lobby_invite_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"invite_id": "invite-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._accept_lobby_invite_impl(mock_request)
            assert response is mock_response

    def test_decline_lobby_invite_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"invite_id": "invite-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch.object(lobbies, 'lobby_service') as mock_lobby_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_lobby_service.decline_lobby_invite.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._decline_lobby_invite_impl(mock_request)
            assert response is mock_response

    def test_decline_lobby_invite_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"invite_id": "invite-123"})
        with patch.object(lobbies, 'auth_service') as mock_auth_service, \
             patch('lobbies.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = lobbies._decline_lobby_invite_impl(mock_request)
            assert response is mock_response

class TestFriendshipEndpoints:
    def test_send_friend_request_success(self):
        mock_request = make_mock_request({"addressee_id": "user-456"}, headers={"Authorization": "Bearer mock-token"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship = MagicMock()
            mock_friendship.dict.return_value = {"id": "friendship-123"}
            mock_friendship_service.send_friend_request.return_value = mock_friendship
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._send_friend_request_impl(mock_request)
            assert response is mock_response

    def test_accept_friend_request_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"requester_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship_service.accept_friend_request.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._accept_friend_request_impl(mock_request)
            assert response is mock_response

    def test_accept_friend_request_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"requester_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._accept_friend_request_impl(mock_request)
            assert response is mock_response

    def test_reject_friend_request_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"requester_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship_service.reject_friend_request.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._reject_friend_request_impl(mock_request)
            assert response is mock_response

    def test_reject_friend_request_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"requester_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._reject_friend_request_impl(mock_request)
            assert response is mock_response

    def test_get_friends_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship_service.get_friends.return_value = ["user-456", "user-789"]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._get_friends_impl(mock_request)
            assert response is mock_response

    def test_get_friends_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="GET")
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._get_friends_impl(mock_request)
            assert response is mock_response

    def test_get_pending_requests_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_request_obj = MagicMock()
            mock_request_obj.dict.return_value = {"id": "request-123"}
            mock_friendship_service.get_pending_requests.return_value = [mock_request_obj]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._get_pending_requests_impl(mock_request)
            assert response is mock_response

    def test_get_pending_requests_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="GET")
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._get_pending_requests_impl(mock_request)
            assert response is mock_response

    def test_get_sent_requests_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET")
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_request_obj = MagicMock()
            mock_request_obj.dict.return_value = {"id": "request-123"}
            mock_friendship_service.get_sent_requests.return_value = [mock_request_obj]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._get_sent_requests_impl(mock_request)
            assert response is mock_response

    def test_get_sent_requests_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="GET")
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._get_sent_requests_impl(mock_request)
            assert response is mock_response

    def test_remove_friend_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="DELETE", route_params={"friend_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship_service.remove_friend.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._remove_friend_impl(mock_request)
            assert response is mock_response

    def test_remove_friend_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="DELETE", route_params={"friend_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._remove_friend_impl(mock_request)
            assert response is mock_response

    def test_block_user_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"user_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship = MagicMock()
            mock_friendship.dict.return_value = {"id": "friendship-123"}
            mock_friendship_service.block_user.return_value = mock_friendship
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._block_user_impl(mock_request)
            assert response is mock_response

    def test_block_user_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"user_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._block_user_impl(mock_request)
            assert response is mock_response

    def test_unblock_user_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="POST", route_params={"user_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship_service.unblock_user.return_value = True
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._unblock_user_impl(mock_request)
            assert response is mock_response

    def test_unblock_user_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="POST", route_params={"user_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._unblock_user_impl(mock_request)
            assert response is mock_response

    def test_check_friendship_success(self):
        mock_request = make_mock_request(headers={"Authorization": "Bearer mock-token"}, method="GET", route_params={"user_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch.object(friends, 'friendship_service') as mock_friendship_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_friendship_service.are_friends.return_value = True
            mock_friendship_service.is_blocked.return_value = False
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._check_friendship_impl(mock_request)
            assert response is mock_response

    def test_check_friendship_unauthorized(self):
        mock_request = make_mock_request(headers={}, method="GET", route_params={"user_id": "user-456"})
        with patch.object(friends, 'auth_service') as mock_auth_service, \
             patch('friends.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = friends._check_friendship_impl(mock_request)
            assert response is mock_response

class TestLeaderboardEndpoints:
    def test_get_player_leaderboard_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_player = MagicMock()
            mock_player.dict.return_value = {"id": "player-123"}
            mock_leaderboard_service.get_player_leaderboard.return_value = [mock_player]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_player_leaderboard_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_leaderboard_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_dungeon = MagicMock()
            mock_dungeon.dict.return_value = {"id": "dungeon-123"}
            mock_leaderboard_service.get_dungeon_leaderboard.return_value = [mock_dungeon]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_dungeon_leaderboard_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_leaderboard_internal_error(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_leaderboard_service.get_dungeon_leaderboard.side_effect = Exception("fail")
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_dungeon_leaderboard_impl(mock_request)
            assert response is mock_response

    def test_get_player_rank_success(self):
        mock_request = make_mock_request(method="GET", route_params={"user_id": "user-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_leaderboard_service.get_player_rank.return_value = 5
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_player_rank_impl(mock_request)
            assert response is mock_response

    def test_get_player_rank_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"user_id": "user-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_leaderboard_service.get_player_rank.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_player_rank_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_rank_success(self):
        mock_request = make_mock_request(method="GET", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_leaderboard_service.get_dungeon_rank.return_value = 3
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_dungeon_rank_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_rank_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_leaderboard_service.get_dungeon_rank.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_dungeon_rank_impl(mock_request)
            assert response is mock_response

    def test_get_player_score_success(self):
        mock_request = make_mock_request(method="GET", route_params={"user_id": "user-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_score = MagicMock()
            mock_score.dict.return_value = {"score": 1000}
            mock_leaderboard_service.get_player_score.return_value = mock_score
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_player_score_impl(mock_request)
            assert response is mock_response

    def test_get_player_score_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"user_id": "user-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_leaderboard_service.get_player_score.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_player_score_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_score_success(self):
        mock_request = make_mock_request(method="GET", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_score = MagicMock()
            mock_score.dict.return_value = {"score": 500}
            mock_leaderboard_service.get_dungeon_score.return_value = mock_score
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_dungeon_score_impl(mock_request)
            assert response is mock_response

    def test_get_dungeon_score_not_found(self):
        mock_request = make_mock_request(method="GET", route_params={"dungeon_id": "dungeon-123"})
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_leaderboard_service.get_dungeon_score.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_dungeon_score_impl(mock_request)
            assert response is mock_response

    def test_get_top_creators_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_creator = MagicMock()
            mock_creator.dict.return_value = {"id": "creator-123"}
            mock_leaderboard_service.get_top_creators.return_value = [mock_creator]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_top_creators_impl(mock_request)
            assert response is mock_response

    def test_get_most_played_dungeons_success(self):
        mock_request = make_mock_request(method="GET")
        mock_request.params = {"limit": "10"}
        with patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_dungeon = MagicMock()
            mock_dungeon.dict.return_value = {"id": "dungeon-123"}
            mock_leaderboard_service.get_most_played_dungeons.return_value = [mock_dungeon]
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._get_most_played_dungeons_impl(mock_request)
            assert response is mock_response

    def test_update_player_score_success(self):
        mock_request = make_mock_request({
            "user_id": "user-123",
            "username": "testuser",
            "score": 1000,
            "dungeons_completed": 5,
            "dungeons_created": 2,
            "average_rating": 4.5
        }, headers={"Authorization": "Bearer mock-token"}, method="POST")
        with patch.object(leaderboard, 'auth_service') as mock_auth_service, \
             patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_leaderboard_service.update_player_score.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._update_player_score_impl(mock_request)
            assert response is mock_response

    def test_update_player_score_unauthorized(self):
        mock_request = make_mock_request({
            "user_id": "user-123",
            "username": "testuser"
        }, headers={}, method="POST")
        with patch.object(leaderboard, 'auth_service') as mock_auth_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._update_player_score_impl(mock_request)
            assert response is mock_response

    def test_update_player_score_missing_fields(self):
        mock_request = make_mock_request({
            "user_id": "user-123"
        }, headers={"Authorization": "Bearer mock-token"}, method="POST")
        with patch.object(leaderboard, 'auth_service') as mock_auth_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._update_player_score_impl(mock_request)
            assert response is mock_response

    def test_update_dungeon_score_success(self):
        mock_request = make_mock_request({
            "dungeon_id": "dungeon-123",
            "dungeon_name": "Test Dungeon",
            "creator_username": "testuser",
            "score": 500,
            "play_count": 25,
            "average_rating": 4.2,
            "total_ratings": 10
        }, headers={"Authorization": "Bearer mock-token"}, method="POST")
        with patch.object(leaderboard, 'auth_service') as mock_auth_service, \
             patch.object(leaderboard, 'leaderboard_service') as mock_leaderboard_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_leaderboard_service.update_dungeon_score.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._update_dungeon_score_impl(mock_request)
            assert response is mock_response

    def test_update_dungeon_score_unauthorized(self):
        mock_request = make_mock_request({
            "dungeon_id": "dungeon-123",
            "dungeon_name": "Test Dungeon",
            "creator_username": "testuser"
        }, headers={}, method="POST")
        with patch.object(leaderboard, 'auth_service') as mock_auth_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_auth_service.get_current_user.return_value = None
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._update_dungeon_score_impl(mock_request)
            assert response is mock_response

    def test_update_dungeon_score_missing_fields(self):
        mock_request = make_mock_request({
            "dungeon_id": "dungeon-123"
        }, headers={"Authorization": "Bearer mock-token"}, method="POST")
        with patch.object(leaderboard, 'auth_service') as mock_auth_service, \
             patch('leaderboard.func.HttpResponse') as MockHttpResponse:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth_service.get_current_user.return_value = mock_user
            mock_response = MagicMock()
            MockHttpResponse.return_value = mock_response
            response = leaderboard._update_dungeon_score_impl(mock_request)
            assert response is mock_response 