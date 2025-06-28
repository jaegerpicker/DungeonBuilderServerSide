from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class LobbyStatus(str, Enum):
    WAITING = "waiting"
    IN_GAME = "in_game"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LobbyCreate(BaseModel):
    name: str
    dungeon_id: str
    max_players: int = 4
    is_public: bool = True
    password: Optional[str] = None

class LobbyInvite(BaseModel):
    id: str
    lobby_id: str
    inviter_id: str
    invitee_id: str
    created_at: datetime
    expires_at: datetime
    is_accepted: Optional[bool] = None

class Lobby(BaseModel):
    id: str
    name: str
    creator_id: str
    dungeon_id: str
    max_players: int
    current_players: int = 0
    is_public: bool
    password: Optional[str] = None
    status: LobbyStatus = LobbyStatus.WAITING
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None 