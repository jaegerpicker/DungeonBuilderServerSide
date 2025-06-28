import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from models.user import User, UserCreate

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.environ.get("JWT_SECRET")
        self.algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.environ.get("JWT_EXPIRATION_MINUTES", "60"))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def authenticate_user(self, db_service, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        # Query user by username
        query = "SELECT * FROM c WHERE c.username = @username"
        parameters = [{"name": "@username", "value": username}]
        users = db_service.query_items(db_service.users_container, query, parameters)
        
        if not users:
            return None
        
        user_data = users[0]
        if not self.verify_password(password, user_data["hashed_password"]):
            return None
        
        return User(**user_data)

    def get_current_user(self, db_service, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        username = payload.get("sub")
        if username is None:
            return None
        
        # Query user by username
        query = "SELECT * FROM c WHERE c.username = @username"
        parameters = [{"name": "@username", "value": username}]
        users = db_service.query_items(db_service.users_container, query, parameters)
        
        if not users:
            return None
        
        return User(**users[0]) 