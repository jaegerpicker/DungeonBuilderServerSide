from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlayerScore(BaseModel):
    id: str
    user_id: str
    username: str
    total_score: int
    dungeons_completed: int
    dungeons_created: int
    average_rating: float
    last_updated: datetime

class DungeonScore(BaseModel):
    id: str
    dungeon_id: str
    dungeon_name: str
    creator_username: str
    total_score: int
    play_count: int
    average_rating: float
    total_ratings: int
    last_updated: datetime 