from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class DungeonDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class DungeonStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class DungeonCreate(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: DungeonDifficulty = DungeonDifficulty.MEDIUM
    dungeon_data: Dict[str, Any]  # JSON serialized dungeon
    tags: List[str] = []
    is_public: bool = True

class DungeonRating(BaseModel):
    id: str
    dungeon_id: str
    user_id: str
    rating: int  # 1-5 stars
    comment: Optional[str] = None
    created_at: datetime

class Dungeon(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    creator_id: str
    difficulty: DungeonDifficulty
    dungeon_data: Dict[str, Any]
    tags: List[str]
    is_public: bool
    status: DungeonStatus
    average_rating: float = 0.0
    total_ratings: int = 0
    play_count: int = 0
    created_at: datetime
    updated_at: datetime 