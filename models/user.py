from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    PLAYER = "player"
    ADMIN = "admin"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    id: str
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    level: int = 1
    experience: int = 0
    total_score: int = 0
    dungeons_created: int = 0
    dungeons_completed: int = 0
    guild_id: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    hashed_password: str
    display_name: Optional[str] = None
    role: UserRole = UserRole.PLAYER
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None 