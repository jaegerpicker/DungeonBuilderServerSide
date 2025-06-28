import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.auth import AuthService
from services.database import DatabaseService
from services.user_service import UserService
from services.dungeon_service import DungeonService
from services.guild_service import GuildService
from services.lobby_service import LobbyService
from services.friendship_service import FriendshipService
from services.leaderboard_service import LeaderboardService
from models.user import User, UserCreate
from models.dungeon import Dungeon, DungeonCreate
from models.guild import Guild, GuildCreate
from models.lobby import Lobby, LobbyCreate
from models.friendship import Friendship, FriendshipRequest
from models.leaderboard import PlayerScore


class TestUserWorkflow:
    """Integration tests for user registration and authentication workflow."""

    def test_complete_user_registration_workflow(self, database_service, auth_service):
        """Test complete user registration workflow."""
        user_service = UserService(database_service, auth_service)
        
        # Step 1: Register a new user
        with patch.object(database_service, 'query_items') as mock_query:
            mock_query.return_value = []  # No existing user
            
            with patch.object(database_service, 'create_item') as mock_create:
                mock_create.return_value = {
                    "id": "new-user-123",
                    "username": "newuser",
                    "email": "new@example.com",
                    "hashed_password": "hashed_password",
                    "display_name": "New User",
                    "role": "player",
                    "created_at": datetime.utcnow().isoformat(),
                    "last_login": None
                }
                
                user_create = UserCreate(
                    username="newuser",
                    email="new@example.com",
                    password="password123",
                    display_name="New User"
                )
                result = user_service.create_user(user_create)
                
                assert result is not None
                assert result.id == "new-user-123"

    def test_user_login_and_profile_workflow(self, database_service, auth_service, sample_user):
        """Test user login and profile retrieval workflow."""
        user_service = UserService(database_service, auth_service)
        
        # Step 1: Login user
        with patch.object(database_service, 'query_items') as mock_query:
            user_dict = sample_user.model_dump()
            user_dict["display_name"] = user_dict.get("display_name", user_dict["username"])
            mock_query.return_value = [user_dict]
            
            # Test getting user by username
            user = user_service.get_user_by_username("testuser")
            assert user is not None
            assert user.username == "testuser"
            
            # Test getting user profile
            profile = user_service.get_user_profile(user.id)
            assert profile is not None
            assert profile.username == "testuser"


class TestDungeonWorkflow:
    """Integration tests for dungeon creation and management workflow."""

    def test_complete_dungeon_creation_workflow(self, database_service, sample_user):
        """Test complete dungeon creation workflow."""
        dungeon_service = DungeonService(database_service)
        
        # Step 1: Create a dungeon
        dungeon_data = DungeonCreate(
            name="Test Dungeon",
            description="A test dungeon",
            dungeon_data={
                "rooms": [{"id": 1, "type": "entrance", "position": {"x": 0, "y": 0}}],
                "monsters": [{"id": 1, "type": "goblin", "position": {"x": 0.5, "y": 0.5}}],
                "traps": [],
                "treasures": [{"id": 1, "type": "gold", "position": {"x": 1, "y": 1}}]
            },
            difficulty="medium",
            tags=["test", "tutorial"],
            is_public=True
        )
        
        with patch.object(database_service, 'create_item') as mock_create:
            mock_create.return_value = {
                "id": "new-dungeon-123",
                "name": "Test Dungeon",
                "description": "A test dungeon",
                "creator_id": sample_user.id,
                "difficulty": "medium",
                "dungeon_data": dungeon_data.dungeon_data,
                "tags": ["test", "tutorial"],
                "is_public": True,
                "status": "draft",
                "average_rating": 0.0,
                "total_ratings": 0,
                "play_count": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            create_result = dungeon_service.create_dungeon(dungeon_data, sample_user.id)
            
            assert create_result is not None
            assert create_result.id == "new-dungeon-123"

    def test_dungeon_rating_workflow(self, database_service, sample_dungeon):
        """Test dungeon rating workflow."""
        dungeon_service = DungeonService(database_service)
        
        # Step 1: Rate the dungeon
        with patch.object(database_service, 'get_item') as mock_get:
            mock_get.return_value = sample_dungeon.model_dump()
            
            with patch.object(database_service, 'query_items') as mock_query:
                mock_query.return_value = []  # No existing rating
                
                with patch.object(database_service, 'create_item') as mock_create:
                    mock_create.return_value = {
                        "id": "rating-123",
                        "dungeon_id": sample_dungeon.id,
                        "user_id": "user-123",
                        "rating": 5,
                        "comment": "Great dungeon!",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    
                    rating_result = dungeon_service.rate_dungeon(sample_dungeon.id, "user-123", 5)
                    
                    assert rating_result is not None
                    assert rating_result.rating == 5


class TestGuildWorkflow:
    """Integration tests for guild creation and management workflow."""

    def test_complete_guild_creation_workflow(self, database_service, sample_user):
        """Test complete guild creation workflow."""
        guild_service = GuildService(database_service)
        
        # Step 1: Create a guild
        guild_data = GuildCreate(
            name="Test Guild",
            description="A test guild",
            max_members=50,
            is_public=True
        )
        
        with patch.object(database_service, 'query_items') as mock_query:
            mock_query.return_value = []  # No existing guild with same name
            
            with patch.object(database_service, 'create_item') as mock_create:
                mock_create.return_value = {
                    "id": "new-guild-123",
                    "name": "Test Guild",
                    "description": "A test guild",
                    "leader_id": sample_user.id,
                    "max_members": 50,
                    "current_members": 1,
                    "is_public": True,
                    "total_score": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                create_result = guild_service.create_guild(guild_data, sample_user.id)
                
                assert create_result is not None
                assert create_result.id == "new-guild-123"

    def test_guild_member_management_workflow(self, database_service, sample_guild):
        """Test guild member management workflow."""
        guild_service = GuildService(database_service)
        
        # Step 1: Add a member to the guild
        guild_dict = sample_guild.model_dump()
        guild_dict["members"] = ["existing-member-123"]
        with patch.object(database_service, 'query_items') as mock_query:
            # First call returns the guild, second call returns empty list for existing members check
            mock_query.side_effect = [[guild_dict], []]
            with patch.object(database_service, 'update_item') as mock_update:
                updated_guild = guild_dict.copy()
                updated_guild["members"].append("new-member-123")
                updated_guild["current_members"] = len(updated_guild["members"])
                mock_update.return_value = updated_guild
                result = guild_service.add_member_to_guild(sample_guild.id, "new-member-123", "member")
                assert result is True


class TestLobbyWorkflow:
    """Integration tests for lobby creation and management workflow."""

    def test_complete_lobby_creation_workflow(self, database_service, sample_user):
        """Test complete lobby creation workflow."""
        lobby_service = LobbyService(database_service)
        
        # Step 1: Create a lobby
        lobby_data = LobbyCreate(
            name="Test Lobby",
            description="A test lobby",
            dungeon_id="dungeon-123",
            dungeon_name="Test Dungeon",
            max_players=4,
            is_public=True,
            password=None
        )
        
        with patch.object(database_service, 'create_item') as mock_create:
            mock_create.return_value = {
                "id": "new-lobby-123",
                "name": "Test Lobby",
                "description": "A test lobby",
                "creator_id": sample_user.id,
                "dungeon_id": "dungeon-123",
                "dungeon_name": "Test Dungeon",
                "max_players": 4,
                "current_players": 1,
                "is_public": True,
                "password": None,
                "status": "waiting",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            create_result = lobby_service.create_lobby(lobby_data, sample_user.id)
            
            assert create_result is not None
            assert create_result.id == "new-lobby-123"

    def test_lobby_join_workflow(self, database_service, sample_lobby):
        """Test lobby join workflow."""
        lobby_service = LobbyService(database_service)
        
        # Step 1: Join the lobby
        lobby_dict = sample_lobby.model_dump()
        with patch.object(database_service, 'get_item') as mock_get:
            mock_get.return_value = lobby_dict
            with patch.object(database_service, 'query_items') as mock_query:
                mock_query.return_value = [lobby_dict]
                with patch.object(database_service, 'update_item') as mock_update:
                    updated_lobby = lobby_dict.copy()
                    updated_lobby["current_players"] = 2
                    mock_update.return_value = updated_lobby
                    result = lobby_service.join_lobby(sample_lobby.id, "new-player-123")
                    assert result is True


class TestFriendshipWorkflow:
    """Integration tests for friendship management workflow."""

    def test_complete_friendship_workflow(self, database_service, sample_user):
        """Test complete friendship workflow."""
        friendship_service = FriendshipService(database_service)
        
        # Step 1: Send friend request
        with patch.object(database_service, 'query_items') as mock_query:
            mock_query.return_value = []  # No existing friendship
            
            with patch.object(database_service, 'create_item') as mock_create:
                mock_create.return_value = {
                    "id": "new-friendship-123",
                    "requester_id": sample_user.id,
                    "addressee_id": "recipient-123",
                    "status": "pending",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                request_result = friendship_service.send_friend_request(
                    sample_user.id, "recipient-123"
                )
                
                assert request_result is not None
                assert request_result.id == "new-friendship-123"


class TestLeaderboardWorkflow:
    """Integration tests for leaderboard management workflow."""

    def test_complete_leaderboard_workflow(self, database_service, sample_user):
        """Test complete leaderboard workflow."""
        leaderboard_service = LeaderboardService(database_service)
        
        # Step 1: Update player score
        with patch.object(database_service, 'query_items') as mock_query:
            mock_query.return_value = []
            
            with patch.object(database_service, 'create_item') as mock_create:
                mock_create.return_value = {
                    "id": "new-entry-123",
                    "user_id": sample_user.id,
                    "username": sample_user.username,
                    "total_score": 1500,
                    "dungeons_completed": 10,
                    "dungeons_created": 5,
                    "average_rating": 4.5,
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                # update_player_score doesn't return anything, so test the creation
                leaderboard_service.update_player_score(sample_user.id, sample_user.username, 1500)
                
                # Verify the create_item was called
                mock_create.assert_called_once()

    def test_player_rank_workflow(self, database_service, sample_leaderboard_entry):
        """Test player rank workflow."""
        leaderboard_service = LeaderboardService(database_service)
        
        # Step 1: Get player rank
        with patch.object(database_service, 'query_items') as mock_query:
            # get_player_rank returns an integer rank, not a dict
            mock_query.return_value = [1]  # Rank 1

            rank_result = leaderboard_service.get_player_rank(sample_leaderboard_entry.user_id)

            assert rank_result is not None
            assert isinstance(rank_result, int)
            assert rank_result > 0


class TestCrossServiceWorkflow:
    """Integration tests for cross-service workflows."""

    def test_user_dungeon_guild_workflow(self, database_service, auth_service, sample_user):
        """Test workflow involving user, dungeon, and guild services."""
        user_service = UserService(database_service, auth_service)
        dungeon_service = DungeonService(database_service)
        guild_service = GuildService(database_service)
        
        # Step 1: Register user
        with patch.object(database_service, 'query_items') as mock_query:
            mock_query.return_value = []
            
            with patch.object(database_service, 'create_item') as mock_create:
                mock_create.return_value = {
                    "id": "new-user-123",
                    "username": "newuser",
                    "email": "new@example.com",
                    "hashed_password": "hashed_password",
                    "display_name": "New User",
                    "role": "player",
                    "created_at": datetime.utcnow().isoformat(),
                    "last_login": None
                }
                
                user_create = UserCreate(
                    username="newuser",
                    email="new@example.com",
                    password="password123",
                    display_name="New User"
                )
                user_result = user_service.create_user(user_create)
                
                assert user_result is not None
                assert user_result.id == "new-user-123"
                
                # Step 2: Create dungeon
                dungeon_data = DungeonCreate(
                    name="Test Dungeon",
                    description="A test dungeon",
                    dungeon_data={"rooms": [], "monsters": [], "traps": [], "treasures": []},
                    difficulty="easy",
                    tags=["test"],
                    is_public=True
                )
                
                mock_create.return_value = {
                    "id": "new-dungeon-123",
                    "name": "Test Dungeon",
                    "description": "A test dungeon",
                    "creator_id": user_result.id,
                    "difficulty": "easy",
                    "dungeon_data": {"rooms": [], "monsters": [], "traps": [], "treasures": []},
                    "tags": ["test"],
                    "is_public": True,
                    "status": "draft",
                    "average_rating": 0.0,
                    "total_ratings": 0,
                    "play_count": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                dungeon_result = dungeon_service.create_dungeon(dungeon_data, user_result.id)
                
                assert dungeon_result is not None
                assert dungeon_result.creator_id == user_result.id
                
                # Step 3: Create guild
                guild_data = GuildCreate(
                    name="Test Guild",
                    description="A test guild",
                    max_members=50,
                    is_public=True
                )
                
                mock_create.return_value = {
                    "id": "new-guild-123",
                    "name": "Test Guild",
                    "description": "A test guild",
                    "leader_id": user_result.id,
                    "max_members": 50,
                    "current_members": 1,
                    "is_public": True,
                    "total_score": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                guild_result = guild_service.create_guild(guild_data, user_result.id)
                
                assert guild_result is not None
                assert guild_result.leader_id == user_result.id 