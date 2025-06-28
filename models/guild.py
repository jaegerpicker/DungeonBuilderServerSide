from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GuildRole(str, Enum):
    MEMBER = "member"
    OFFICER = "officer"
    LEADER = "leader"

class GuildCreate(BaseModel):
    name: str
    description: Optional[str] = None
    max_members: int = 50
    is_public: bool = True

class GuildMember(BaseModel):
    id: str
    guild_id: str
    user_id: str
    role: GuildRole = GuildRole.MEMBER
    joined_at: datetime
    contribution_points: int = 0

class Guild(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    leader_id: str
    max_members: int
    current_members: int = 0
    is_public: bool
    total_score: int = 0
    created_at: datetime
    updated_at: datetime 