from datetime import datetime
from typing import List, Optional
from models.leaderboard import PlayerScore, DungeonScore
from services.database import DatabaseService

class LeaderboardService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def update_player_score(self, user_id: str, username: str, score: int, dungeons_completed: int = 0, dungeons_created: int = 0, average_rating: float = 0.0):
        """Update or create player score"""
        # Check if player score already exists
        query = "SELECT * FROM c WHERE c.user_id = @userId AND c.username IS NOT NULL"
        parameters = [{"name": "@userId", "value": user_id}]
        existing_scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        
        score_data = {
            "user_id": user_id,
            "username": username,
            "total_score": score,
            "dungeons_completed": dungeons_completed,
            "dungeons_created": dungeons_created,
            "average_rating": average_rating,
            "last_updated": datetime.utcnow().isoformat(),
            "partitionKey": "player_scores"
        }
        
        if existing_scores:
            # Update existing score
            existing_score = existing_scores[0]
            self.db_service.update_item(
                self.db_service.leaderboard_container,
                existing_score["id"],
                "player_scores",  # partition key
                {
                    "total_score": score,
                    "dungeons_completed": dungeons_completed,
                    "dungeons_created": dungeons_created,
                    "average_rating": average_rating,
                    "last_updated": datetime.utcnow().isoformat()
                }
            )
        else:
            # Create new score
            self.db_service.create_item(self.db_service.leaderboard_container, score_data)

    def update_dungeon_score(self, dungeon_id: str, dungeon_name: str, creator_username: str, score: int, play_count: int, average_rating: float, total_ratings: int):
        """Update or create dungeon score"""
        # Check if dungeon score already exists
        query = "SELECT * FROM c WHERE c.dungeon_id = @dungeonId AND c.dungeon_name IS NOT NULL"
        parameters = [{"name": "@dungeonId", "value": dungeon_id}]
        existing_scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        
        score_data = {
            "dungeon_id": dungeon_id,
            "dungeon_name": dungeon_name,
            "creator_username": creator_username,
            "total_score": score,
            "play_count": play_count,
            "average_rating": average_rating,
            "total_ratings": total_ratings,
            "last_updated": datetime.utcnow().isoformat(),
            "partitionKey": "dungeon_scores"
        }
        
        if existing_scores:
            # Update existing score
            existing_score = existing_scores[0]
            self.db_service.update_item(
                self.db_service.leaderboard_container,
                existing_score["id"],
                "dungeon_scores",  # partition key
                {
                    "total_score": score,
                    "play_count": play_count,
                    "average_rating": average_rating,
                    "total_ratings": total_ratings,
                    "last_updated": datetime.utcnow().isoformat()
                }
            )
        else:
            # Create new score
            self.db_service.create_item(self.db_service.leaderboard_container, score_data)

    def get_player_leaderboard(self, limit: int = 50) -> List[PlayerScore]:
        """Get top players by total score"""
        query = """
        SELECT * FROM c 
        WHERE c.username IS NOT NULL AND c.user_id IS NOT NULL
        ORDER BY c.total_score DESC, c.dungeons_completed DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [{"name": "@limit", "value": limit}]
        
        scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        return [PlayerScore(**score) for score in scores]

    def get_dungeon_leaderboard(self, limit: int = 50) -> List[DungeonScore]:
        """Get top dungeons by average rating and play count"""
        query = """
        SELECT * FROM c 
        WHERE c.dungeon_name IS NOT NULL AND c.dungeon_id IS NOT NULL
        ORDER BY c.average_rating DESC, c.play_count DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [{"name": "@limit", "value": limit}]
        
        scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        return [DungeonScore(**score) for score in scores]

    def get_player_rank(self, user_id: str) -> Optional[int]:
        """Get player's rank in the leaderboard"""
        query = """
        SELECT VALUE COUNT(1) + 1 FROM c 
        WHERE c.username IS NOT NULL AND c.user_id IS NOT NULL
        AND c.total_score > (SELECT VALUE c2.total_score FROM c c2 WHERE c2.user_id = @userId)
        """
        parameters = [{"name": "@userId", "value": user_id}]
        
        result = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        if result:
            return result[0]
        return None

    def get_dungeon_rank(self, dungeon_id: str) -> Optional[int]:
        """Get dungeon's rank in the leaderboard"""
        query = """
        SELECT VALUE COUNT(1) + 1 FROM c 
        WHERE c.dungeon_name IS NOT NULL AND c.dungeon_id IS NOT NULL
        AND c.average_rating > (SELECT VALUE c2.average_rating FROM c c2 WHERE c2.dungeon_id = @dungeonId)
        """
        parameters = [{"name": "@dungeonId", "value": dungeon_id}]
        
        result = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        if result:
            return result[0]
        return None

    def get_player_score(self, user_id: str) -> Optional[PlayerScore]:
        """Get player's score"""
        query = "SELECT * FROM c WHERE c.user_id = @userId AND c.username IS NOT NULL"
        parameters = [{"name": "@userId", "value": user_id}]
        
        scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        if scores:
            return PlayerScore(**scores[0])
        return None

    def get_dungeon_score(self, dungeon_id: str) -> Optional[DungeonScore]:
        """Get dungeon's score"""
        query = "SELECT * FROM c WHERE c.dungeon_id = @dungeonId AND c.dungeon_name IS NOT NULL"
        parameters = [{"name": "@dungeonId", "value": dungeon_id}]
        
        scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        if scores:
            return DungeonScore(**scores[0])
        return None

    def get_top_creators(self, limit: int = 20) -> List[PlayerScore]:
        """Get top dungeon creators"""
        query = """
        SELECT * FROM c 
        WHERE c.username IS NOT NULL AND c.user_id IS NOT NULL
        ORDER BY c.dungeons_created DESC, c.average_rating DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [{"name": "@limit", "value": limit}]
        
        scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        return [PlayerScore(**score) for score in scores]

    def get_most_played_dungeons(self, limit: int = 20) -> List[DungeonScore]:
        """Get most played dungeons"""
        query = """
        SELECT * FROM c 
        WHERE c.dungeon_name IS NOT NULL AND c.dungeon_id IS NOT NULL
        ORDER BY c.play_count DESC, c.average_rating DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [{"name": "@limit", "value": limit}]
        
        scores = self.db_service.query_items(self.db_service.leaderboard_container, query, parameters)
        return [DungeonScore(**score) for score in scores] 