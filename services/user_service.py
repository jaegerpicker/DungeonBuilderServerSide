from datetime import datetime
from typing import List, Optional
from models.user import User, UserCreate, UserProfile
from services.database import DatabaseService
from services.auth import AuthService

class UserService:
    def __init__(self, db_service: DatabaseService, auth_service: AuthService):
        self.db_service = db_service
        self.auth_service = auth_service

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if username already exists
        query = "SELECT * FROM c WHERE c.username = @username"
        parameters = [{"name": "@username", "value": user_create.username}]
        existing_users = self.db_service.query_items(self.db_service.users_container, query, parameters)
        
        if existing_users:
            raise ValueError("Username already exists")
        
        # Check if email already exists
        query = "SELECT * FROM c WHERE c.email = @email"
        parameters = [{"name": "@email", "value": user_create.email}]
        existing_users = self.db_service.query_items(self.db_service.users_container, query, parameters)
        
        if existing_users:
            raise ValueError("Email already exists")
        
        # Create user
        user_data = {
            "username": user_create.username,
            "email": user_create.email,
            "hashed_password": self.auth_service.get_password_hash(user_create.password),
            "display_name": user_create.display_name or user_create.username,
            "partitionKey": user_create.username
        }
        
        created_user = self.db_service.create_item(self.db_service.users_container, user_data)
        return User(**created_user)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        # Query user by ID
        query = "SELECT * FROM c WHERE c.id = @userId"
        parameters = [{"name": "@userId", "value": user_id}]
        users = self.db_service.query_items(self.db_service.users_container, query, parameters)
        
        if not users:
            return None
        
        return User(**users[0])

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        query = "SELECT * FROM c WHERE c.username = @username"
        parameters = [{"name": "@username", "value": username}]
        users = self.db_service.query_items(self.db_service.users_container, query, parameters)
        
        if not users:
            return None
        
        return User(**users[0])

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Get additional profile data
        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "level": 1,  # Default values, would be calculated from game data
            "experience": 0,
            "total_score": 0,
            "dungeons_created": 0,
            "dungeons_completed": 0,
            "guild_id": None,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        
        return UserProfile(**profile_data)

    def update_user_profile(self, user_id: str, updates: dict) -> Optional[User]:
        """Update user profile"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update user data
        updated_user = self.db_service.update_item(
            self.db_service.users_container,
            user_id,
            user.username,  # partition key
            updates
        )
        
        return User(**updated_user)

    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login time"""
        try:
            self.db_service.update_item(
                self.db_service.users_container,
                user_id,
                "username",  # partition key placeholder
                {"last_login": datetime.utcnow().isoformat()}
            )
            return True
        except:
            return False

    def search_users(self, search_term: str, limit: int = 10) -> List[UserProfile]:
        """Search users by username or display name"""
        query = """
        SELECT * FROM c 
        WHERE (CONTAINS(c.username, @searchTerm, true) OR CONTAINS(c.display_name, @searchTerm, true))
        AND c.is_active = true
        ORDER BY c.username
        OFFSET 0 LIMIT @limit
        """
        parameters = [
            {"name": "@searchTerm", "value": search_term},
            {"name": "@limit", "value": limit}
        ]
        
        users = self.db_service.query_items(self.db_service.users_container, query, parameters)
        return [UserProfile(**self._convert_to_profile(user)) for user in users]

    def _convert_to_profile(self, user_data: dict) -> dict:
        """Convert user data to profile format"""
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "display_name": user_data.get("display_name"),
            "level": user_data.get("level", 1),
            "experience": user_data.get("experience", 0),
            "total_score": user_data.get("total_score", 0),
            "dungeons_created": user_data.get("dungeons_created", 0),
            "dungeons_completed": user_data.get("dungeons_completed", 0),
            "guild_id": user_data.get("guild_id"),
            "created_at": datetime.fromisoformat(user_data["created_at"]),
            "last_login": datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None
        } 