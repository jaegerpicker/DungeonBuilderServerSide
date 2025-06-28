import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt

# Patch DatabaseService at module level to prevent import-time instantiation
with patch('services.database.DatabaseService', autospec=True) as mock_db_service:
    instance = mock_db_service.return_value
    instance.client = MagicMock()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User, UserRole
from models.dungeon import Dungeon, DungeonDifficulty, DungeonStatus
from models.guild import Guild
from models.lobby import Lobby, LobbyStatus
from models.friendship import Friendship, FriendshipStatus
from models.leaderboard import PlayerScore, DungeonScore
from services.auth import AuthService
from services.database import DatabaseService
from services.user_service import UserService
from services.dungeon_service import DungeonService
from services.guild_service import GuildService
from services.lobby_service import LobbyService
from services.friendship_service import FriendshipService
from services.leaderboard_service import LeaderboardService


@pytest.fixture
def mock_cosmos_client():
    """Mock Cosmos DB client for testing."""
    with patch('azure.cosmos.CosmosClient') as mock_client:
        mock_container = Mock()
        mock_database = Mock()
        mock_database.get_container_client.return_value = mock_container
        mock_client.get_database_client.return_value = mock_database
        yield mock_client


@pytest.fixture
def database_service():
    """Database service with mocked Cosmos DB client."""
    # Create a mock instance instead of calling the real constructor
    mock_service = MagicMock(spec=DatabaseService)
    mock_service.client = MagicMock()
    mock_service.database = MagicMock()
    mock_service.users_container = MagicMock()
    mock_service.dungeons_container = MagicMock()
    mock_service.guilds_container = MagicMock()
    mock_service.lobbies_container = MagicMock()
    mock_service.friendships_container = MagicMock()
    mock_service.ratings_container = MagicMock()
    mock_service.leaderboard_container = MagicMock()
    
    return mock_service


@pytest.fixture
def auth_service():
    """Auth service for testing."""
    return AuthService()


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return User(
        id="test-user-123",
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        display_name="Test User",
        role=UserRole.PLAYER,
        is_active=True,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )


@pytest.fixture
def sample_dungeon():
    """Sample dungeon data for testing."""
    return Dungeon(
        id="test-dungeon-123",
        name="Test Dungeon",
        description="A test dungeon for testing",
        creator_id="test-user-123",
        difficulty=DungeonDifficulty.MEDIUM,
        dungeon_data={
            "rooms": [{"id": 1, "type": "entrance", "position": {"x": 0, "y": 0}}],
            "monsters": [],
            "traps": [],
            "treasures": []
        },
        tags=["test", "medium"],
        is_public=True,
        status=DungeonStatus.PUBLISHED,
        average_rating=4.5,
        total_ratings=10,
        play_count=25,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_guild():
    """Sample guild data for testing."""
    return Guild(
        id="test-guild-123",
        name="Test Guild",
        description="A test guild for testing",
        leader_id="test-user-123",
        max_members=50,
        current_members=5,
        is_public=True,
        total_score=1500,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_lobby():
    """Sample lobby data for testing."""
    return Lobby(
        id="test-lobby-123",
        name="Test Lobby",
        creator_id="test-user-123",
        dungeon_id="test-dungeon-123",
        max_players=4,
        current_players=2,
        is_public=True,
        password=None,
        status=LobbyStatus.WAITING,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_friendship():
    """Sample friendship data for testing."""
    return Friendship(
        id="test-friendship-123",
        requester_id="test-user-123",
        addressee_id="test-user-456",
        status=FriendshipStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_leaderboard_entry():
    """Sample player leaderboard entry for testing."""
    return PlayerScore(
        id="test-entry-123",
        user_id="test-user-123",
        username="testuser",
        total_score=1500,
        dungeons_completed=10,
        dungeons_created=5,
        average_rating=4.5,
        last_updated=datetime.utcnow()
    )


@pytest.fixture
def valid_jwt_token(auth_service, sample_user):
    """Generate a valid JWT token for testing."""
    return auth_service.create_access_token(data={"sub": sample_user.username})


@pytest.fixture
def expired_jwt_token(auth_service, sample_user):
    """Generate an expired JWT token for testing."""
    with patch('services.auth.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = datetime.utcnow() - timedelta(hours=2)
        return auth_service.create_token(sample_user.id, sample_user.username)


@pytest.fixture
def mock_request():
    """Mock HTTP request for testing."""
    request = Mock()
    request.headers = {}
    request.method = "GET"
    request.url = "http://localhost:7071/api/test"
    return request


@pytest.fixture
def mock_context():
    """Mock Azure Functions context for testing."""
    context = Mock()
    context.function_name = "test_function"
    context.invocation_id = "test-invocation-123"
    return context


@pytest.fixture
def test_settings():
    """Test environment settings."""
    return {
        "COSMOS_DB_ENDPOINT": "https://test-cosmos.documents.azure.com:443/",
        "COSMOS_DB_KEY": "test-key",
        "COSMOS_DB_DATABASE": "TestDungeonBuilderDB",
        "JWT_SECRET": "test-jwt-secret-key-for-testing-only",
        "JWT_ALGORITHM": "HS256",
        "JWT_EXPIRATION_MINUTES": "60"
    }


@pytest.fixture(autouse=True)
def setup_test_environment(test_settings):
    """Set up test environment variables."""
    for key, value in test_settings.items():
        os.environ[key] = value
    yield
    # Clean up environment variables after tests
    for key in test_settings.keys():
        if key in os.environ:
            del os.environ[key]


@pytest.fixture(autouse=True, scope='session')
def mock_database_service():
    with patch('services.database.DatabaseService', autospec=True) as mock_db_service:
        # Optionally, set up default return values for methods if needed
        instance = mock_db_service.return_value
        instance.client = MagicMock()
        yield mock_db_service 


@pytest.fixture
def user_service(database_service, auth_service):
    """UserService instance for testing."""
    from services.user_service import UserService
    return UserService(database_service, auth_service) 