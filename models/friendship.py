from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class FriendshipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"

class FriendshipRequest(BaseModel):
    requester_id: str
    addressee_id: str

class Friendship(BaseModel):
    id: str
    requester_id: str
    addressee_id: str
    status: FriendshipStatus
    created_at: datetime
    updated_at: datetime 