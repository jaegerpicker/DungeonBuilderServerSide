from datetime import datetime
from typing import List, Optional, Dict, Any
from models.dungeon import Dungeon, DungeonCreate, DungeonRating
from services.database import DatabaseService

class DungeonService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_dungeon(self, dungeon_create: DungeonCreate, creator_id: str) -> Dungeon:
        """Create a new dungeon"""
        dungeon_data = {
            "name": dungeon_create.name,
            "description": dungeon_create.description,
            "creator_id": creator_id,
            "difficulty": dungeon_create.difficulty.value,
            "dungeon_data": dungeon_create.dungeon_data,
            "tags": dungeon_create.tags,
            "is_public": dungeon_create.is_public,
            "status": "draft",
            "average_rating": 0.0,
            "total_ratings": 0,
            "play_count": 0,
            "partitionKey": creator_id
        }
        
        created_dungeon = self.db_service.create_item(self.db_service.dungeons_container, dungeon_data)
        return Dungeon(**created_dungeon)

    def get_dungeon_by_id(self, dungeon_id: str) -> Optional[Dungeon]:
        """Get dungeon by ID"""
        query = "SELECT * FROM c WHERE c.id = @dungeonId"
        parameters = [{"name": "@dungeonId", "value": dungeon_id}]
        dungeons = self.db_service.query_items(self.db_service.dungeons_container, query, parameters)
        
        if not dungeons:
            return None
        
        return Dungeon(**dungeons[0])

    def get_dungeons_by_creator(self, creator_id: str, limit: int = 20) -> List[Dungeon]:
        """Get dungeons created by a specific user"""
        query = """
        SELECT * FROM c 
        WHERE c.creator_id = @creatorId
        ORDER BY c.created_at DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [
            {"name": "@creatorId", "value": creator_id},
            {"name": "@limit", "value": limit}
        ]
        
        dungeons = self.db_service.query_items(self.db_service.dungeons_container, query, parameters)
        return [Dungeon(**dungeon) for dungeon in dungeons]

    def get_public_dungeons(self, limit: int = 20, offset: int = 0, difficulty: Optional[str] = None) -> List[Dungeon]:
        """Get public dungeons with optional filtering"""
        query = "SELECT * FROM c WHERE c.is_public = true AND c.status = 'published'"
        parameters = []
        
        if difficulty:
            query += " AND c.difficulty = @difficulty"
            parameters.append({"name": "@difficulty", "value": difficulty})
        
        query += " ORDER BY c.average_rating DESC, c.play_count DESC OFFSET @offset LIMIT @limit"
        parameters.extend([
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit}
        ])
        
        dungeons = self.db_service.query_items(self.db_service.dungeons_container, query, parameters)
        return [Dungeon(**dungeon) for dungeon in dungeons]

    def search_dungeons(self, search_term: str, limit: int = 20) -> List[Dungeon]:
        """Search dungeons by name, description, or tags"""
        query = """
        SELECT * FROM c 
        WHERE c.is_public = true AND c.status = 'published'
        AND (CONTAINS(c.name, @searchTerm, true) 
             OR CONTAINS(c.description, @searchTerm, true)
             OR ARRAY_CONTAINS(c.tags, @searchTerm))
        ORDER BY c.average_rating DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [
            {"name": "@searchTerm", "value": search_term},
            {"name": "@limit", "value": limit}
        ]
        
        dungeons = self.db_service.query_items(self.db_service.dungeons_container, query, parameters)
        return [Dungeon(**dungeon) for dungeon in dungeons]

    def update_dungeon(self, dungeon_id: str, creator_id: str, updates: Dict[str, Any]) -> Optional[Dungeon]:
        """Update a dungeon"""
        dungeon = self.get_dungeon_by_id(dungeon_id)
        if not dungeon or dungeon.creator_id != creator_id:
            return None
        
        updated_dungeon = self.db_service.update_item(
            self.db_service.dungeons_container,
            dungeon_id,
            creator_id,  # partition key
            updates
        )
        
        return Dungeon(**updated_dungeon)

    def delete_dungeon(self, dungeon_id: str, creator_id: str) -> bool:
        """Delete a dungeon"""
        dungeon = self.get_dungeon_by_id(dungeon_id)
        if not dungeon or dungeon.creator_id != creator_id:
            return False
        
        return self.db_service.delete_item(
            self.db_service.dungeons_container,
            dungeon_id,
            creator_id  # partition key
        )

    def rate_dungeon(self, dungeon_id: str, user_id: str, rating: int, comment: Optional[str] = None) -> DungeonRating:
        """Rate a dungeon (1-5 stars)"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if user already rated this dungeon
        query = "SELECT * FROM c WHERE c.dungeon_id = @dungeonId AND c.user_id = @userId"
        parameters = [
            {"name": "@dungeonId", "value": dungeon_id},
            {"name": "@userId", "value": user_id}
        ]
        existing_ratings = self.db_service.query_items(self.db_service.ratings_container, query, parameters)
        
        rating_data = {
            "dungeon_id": dungeon_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "partitionKey": dungeon_id
        }
        
        if existing_ratings:
            # Update existing rating
            existing_rating = existing_ratings[0]
            updated_rating = self.db_service.update_item(
                self.db_service.ratings_container,
                existing_rating["id"],
                dungeon_id,  # partition key
                {"rating": rating, "comment": comment}
            )
            rating_obj = DungeonRating(**updated_rating)
        else:
            # Create new rating
            created_rating = self.db_service.create_item(self.db_service.ratings_container, rating_data)
            rating_obj = DungeonRating(**created_rating)
        
        # Update dungeon average rating
        self._update_dungeon_rating(dungeon_id)
        
        return rating_obj

    def _update_dungeon_rating(self, dungeon_id: str):
        """Update dungeon's average rating"""
        query = "SELECT * FROM c WHERE c.dungeon_id = @dungeonId"
        parameters = [{"name": "@dungeonId", "value": dungeon_id}]
        ratings = self.db_service.query_items(self.db_service.ratings_container, query, parameters)
        
        if ratings:
            total_rating = sum(r["rating"] for r in ratings)
            average_rating = total_rating / len(ratings)
            
            # Update dungeon
            dungeon = self.get_dungeon_by_id(dungeon_id)
            if dungeon:
                self.db_service.update_item(
                    self.db_service.dungeons_container,
                    dungeon_id,
                    dungeon.creator_id,  # partition key
                    {
                        "average_rating": round(average_rating, 2),
                        "total_ratings": len(ratings)
                    }
                )

    def increment_play_count(self, dungeon_id: str):
        """Increment dungeon play count"""
        dungeon = self.get_dungeon_by_id(dungeon_id)
        if dungeon:
            self.db_service.update_item(
                self.db_service.dungeons_container,
                dungeon_id,
                dungeon.creator_id,  # partition key
                {"play_count": dungeon.play_count + 1}
            ) 