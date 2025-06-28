from datetime import datetime
from typing import List, Optional
from models.guild import Guild, GuildCreate, GuildMember
from services.database import DatabaseService

class GuildService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_guild(self, guild_create: GuildCreate, leader_id: str) -> Guild:
        """Create a new guild"""
        guild_data = {
            "name": guild_create.name,
            "description": guild_create.description,
            "leader_id": leader_id,
            "max_members": guild_create.max_members,
            "current_members": 1,  # Leader is the first member
            "is_public": guild_create.is_public,
            "total_score": 0,
            "partitionKey": leader_id
        }
        
        created_guild = self.db_service.create_item(self.db_service.guilds_container, guild_data)
        
        # Add leader as first member
        member_data = {
            "guild_id": created_guild["id"],
            "user_id": leader_id,
            "role": "leader",
            "contribution_points": 0,
            "partitionKey": created_guild["id"]
        }
        self.db_service.create_item(self.db_service.guilds_container, member_data)
        
        return Guild(**created_guild)

    def get_guild_by_id(self, guild_id: str) -> Optional[Guild]:
        """Get guild by ID"""
        query = "SELECT * FROM c WHERE c.id = @guildId AND c.leader_id IS NOT NULL"
        parameters = [{"name": "@guildId", "value": guild_id}]
        guilds = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        
        if not guilds:
            return None
        
        return Guild(**guilds[0])

    def get_guilds_by_leader(self, leader_id: str) -> List[Guild]:
        """Get guilds led by a specific user"""
        query = "SELECT * FROM c WHERE c.leader_id = @leaderId"
        parameters = [{"name": "@leaderId", "value": leader_id}]
        
        guilds = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        return [Guild(**guild) for guild in guilds]

    def get_public_guilds(self, limit: int = 20) -> List[Guild]:
        """Get public guilds"""
        query = """
        SELECT * FROM c 
        WHERE c.is_public = true AND c.leader_id IS NOT NULL
        ORDER BY c.total_score DESC, c.current_members DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [{"name": "@limit", "value": limit}]
        
        guilds = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        return [Guild(**guild) for guild in guilds]

    def search_guilds(self, search_term: str, limit: int = 20) -> List[Guild]:
        """Search guilds by name or description"""
        query = """
        SELECT * FROM c 
        WHERE c.is_public = true AND c.leader_id IS NOT NULL
        AND (CONTAINS(c.name, @searchTerm, true) OR CONTAINS(c.description, @searchTerm, true))
        ORDER BY c.total_score DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [
            {"name": "@searchTerm", "value": search_term},
            {"name": "@limit", "value": limit}
        ]
        
        guilds = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        return [Guild(**guild) for guild in guilds]

    def get_guild_members(self, guild_id: str) -> List[GuildMember]:
        """Get all members of a guild"""
        query = "SELECT * FROM c WHERE c.guild_id = @guildId AND c.user_id IS NOT NULL"
        parameters = [{"name": "@guildId", "value": guild_id}]
        
        members = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        return [GuildMember(**member) for member in members]

    def add_member_to_guild(self, guild_id: str, user_id: str, role: str = "member") -> bool:
        """Add a member to a guild"""
        guild = self.get_guild_by_id(guild_id)
        if not guild:
            return False
        
        if guild.current_members >= guild.max_members:
            return False
        
        # Check if user is already a member
        query = "SELECT * FROM c WHERE c.guild_id = @guildId AND c.user_id = @userId"
        parameters = [
            {"name": "@guildId", "value": guild_id},
            {"name": "@userId", "value": user_id}
        ]
        existing_members = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        
        if existing_members:
            return False
        
        # Add member
        member_data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "role": role,
            "contribution_points": 0,
            "partitionKey": guild_id
        }
        self.db_service.create_item(self.db_service.guilds_container, member_data)
        
        # Update guild member count
        self.db_service.update_item(
            self.db_service.guilds_container,
            guild_id,
            guild.leader_id,  # partition key
            {"current_members": guild.current_members + 1}
        )
        
        return True

    def remove_member_from_guild(self, guild_id: str, user_id: str, leader_id: str) -> bool:
        """Remove a member from a guild (only leader can do this)"""
        guild = self.get_guild_by_id(guild_id)
        if not guild or guild.leader_id != leader_id:
            return False
        
        # Find and remove member
        query = "SELECT * FROM c WHERE c.guild_id = @guildId AND c.user_id = @userId"
        parameters = [
            {"name": "@guildId", "value": guild_id},
            {"name": "@userId", "value": user_id}
        ]
        members = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        
        if not members:
            return False
        
        member = members[0]
        self.db_service.delete_item(
            self.db_service.guilds_container,
            member["id"],
            guild_id  # partition key
        )
        
        # Update guild member count
        self.db_service.update_item(
            self.db_service.guilds_container,
            guild_id,
            leader_id,  # partition key
            {"current_members": guild.current_members - 1}
        )
        
        return True

    def update_guild(self, guild_id: str, leader_id: str, updates: dict) -> Optional[Guild]:
        """Update guild information (only leader can do this)"""
        guild = self.get_guild_by_id(guild_id)
        if not guild or guild.leader_id != leader_id:
            return None
        
        updated_guild = self.db_service.update_item(
            self.db_service.guilds_container,
            guild_id,
            leader_id,  # partition key
            updates
        )
        
        return Guild(**updated_guild)

    def get_user_guild(self, user_id: str) -> Optional[Guild]:
        """Get the guild that a user belongs to"""
        query = "SELECT * FROM c WHERE c.user_id = @userId AND c.guild_id IS NOT NULL"
        parameters = [{"name": "@userId", "value": user_id}]
        members = self.db_service.query_items(self.db_service.guilds_container, query, parameters)
        
        if not members:
            return None
        
        member = members[0]
        return self.get_guild_by_id(member["guild_id"]) 