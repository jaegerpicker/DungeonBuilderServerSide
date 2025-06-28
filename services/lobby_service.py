from datetime import datetime, timedelta
from typing import List, Optional
from models.lobby import Lobby, LobbyCreate, LobbyInvite
from services.database import DatabaseService

class LobbyService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_lobby(self, lobby_create: LobbyCreate, creator_id: str) -> Lobby:
        """Create a new lobby"""
        lobby_data = {
            "name": lobby_create.name,
            "creator_id": creator_id,
            "dungeon_id": lobby_create.dungeon_id,
            "max_players": lobby_create.max_players,
            "current_players": 1,  # Creator is the first player
            "is_public": lobby_create.is_public,
            "password": lobby_create.password,
            "status": "waiting",
            "partitionKey": creator_id
        }
        
        created_lobby = self.db_service.create_item(self.db_service.lobbies_container, lobby_data)
        return Lobby(**created_lobby)

    def get_lobby_by_id(self, lobby_id: str) -> Optional[Lobby]:
        """Get lobby by ID"""
        query = "SELECT * FROM c WHERE c.id = @lobbyId"
        parameters = [{"name": "@lobbyId", "value": lobby_id}]
        lobbies = self.db_service.query_items(self.db_service.lobbies_container, query, parameters)
        
        if not lobbies:
            return None
        
        return Lobby(**lobbies[0])

    def get_public_lobbies(self, limit: int = 20) -> List[Lobby]:
        """Get public lobbies"""
        query = """
        SELECT * FROM c 
        WHERE c.is_public = true AND c.status = 'waiting'
        ORDER BY c.created_at DESC
        OFFSET 0 LIMIT @limit
        """
        parameters = [{"name": "@limit", "value": limit}]
        
        lobbies = self.db_service.query_items(self.db_service.lobbies_container, query, parameters)
        return [Lobby(**lobby) for lobby in lobbies]

    def get_lobbies_by_creator(self, creator_id: str) -> List[Lobby]:
        """Get lobbies created by a specific user"""
        query = "SELECT * FROM c WHERE c.creator_id = @creatorId ORDER BY c.created_at DESC"
        parameters = [{"name": "@creatorId", "value": creator_id}]
        
        lobbies = self.db_service.query_items(self.db_service.lobbies_container, query, parameters)
        return [Lobby(**lobby) for lobby in lobbies]

    def join_lobby(self, lobby_id: str, user_id: str, password: Optional[str] = None) -> bool:
        """Join a lobby"""
        lobby = self.get_lobby_by_id(lobby_id)
        if not lobby:
            return False
        
        if lobby.status != "waiting":
            return False
        
        if lobby.current_players >= lobby.max_players:
            return False
        
        if lobby.password and lobby.password != password:
            return False
        
        # Update lobby player count
        self.db_service.update_item(
            self.db_service.lobbies_container,
            lobby_id,
            lobby.creator_id,  # partition key
            {"current_players": lobby.current_players + 1}
        )
        
        return True

    def leave_lobby(self, lobby_id: str, user_id: str) -> bool:
        """Leave a lobby"""
        lobby = self.get_lobby_by_id(lobby_id)
        if not lobby:
            return False
        
        if lobby.status != "waiting":
            return False
        
        # Update lobby player count
        self.db_service.update_item(
            self.db_service.lobbies_container,
            lobby_id,
            lobby.creator_id,  # partition key
            {"current_players": max(0, lobby.current_players - 1)}
        )
        
        return True

    def start_lobby(self, lobby_id: str, creator_id: str) -> bool:
        """Start a lobby (only creator can do this)"""
        lobby = self.get_lobby_by_id(lobby_id)
        if not lobby or lobby.creator_id != creator_id:
            return False
        
        if lobby.status != "waiting":
            return False
        
        if lobby.current_players < 1:
            return False
        
        # Update lobby status
        self.db_service.update_item(
            self.db_service.lobbies_container,
            lobby_id,
            creator_id,  # partition key
            {
                "status": "in_game",
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
        return True

    def complete_lobby(self, lobby_id: str, creator_id: str) -> bool:
        """Complete a lobby (only creator can do this)"""
        lobby = self.get_lobby_by_id(lobby_id)
        if not lobby or lobby.creator_id != creator_id:
            return False
        
        if lobby.status != "in_game":
            return False
        
        # Update lobby status
        self.db_service.update_item(
            self.db_service.lobbies_container,
            lobby_id,
            creator_id,  # partition key
            {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        return True

    def cancel_lobby(self, lobby_id: str, creator_id: str) -> bool:
        """Cancel a lobby (only creator can do this)"""
        lobby = self.get_lobby_by_id(lobby_id)
        if not lobby or lobby.creator_id != creator_id:
            return False
        
        if lobby.status not in ["waiting", "in_game"]:
            return False
        
        # Update lobby status
        self.db_service.update_item(
            self.db_service.lobbies_container,
            lobby_id,
            creator_id,  # partition key
            {"status": "cancelled"}
        )
        
        return True

    def create_lobby_invite(self, lobby_id: str, inviter_id: str, invitee_id: str) -> LobbyInvite:
        """Create a lobby invite"""
        lobby = self.get_lobby_by_id(lobby_id)
        if not lobby:
            raise ValueError("Lobby not found")
        
        if lobby.creator_id != inviter_id:
            raise ValueError("Only lobby creator can invite players")
        
        if lobby.status != "waiting":
            raise ValueError("Can only invite to waiting lobbies")
        
        if lobby.current_players >= lobby.max_players:
            raise ValueError("Lobby is full")
        
        invite_data = {
            "lobby_id": lobby_id,
            "inviter_id": inviter_id,
            "invitee_id": invitee_id,
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "is_accepted": None,
            "partitionKey": lobby_id
        }
        
        created_invite = self.db_service.create_item(self.db_service.lobbies_container, invite_data)
        return LobbyInvite(**created_invite)

    def get_lobby_invites(self, user_id: str) -> List[LobbyInvite]:
        """Get lobby invites for a user"""
        query = """
        SELECT * FROM c 
        WHERE c.invitee_id = @userId 
        AND c.lobby_id IS NOT NULL 
        AND c.is_accepted IS NULL
        AND c.expires_at > @now
        ORDER BY c.created_at DESC
        """
        parameters = [
            {"name": "@userId", "value": user_id},
            {"name": "@now", "value": datetime.utcnow().isoformat()}
        ]
        
        invites = self.db_service.query_items(self.db_service.lobbies_container, query, parameters)
        return [LobbyInvite(**invite) for invite in invites]

    def accept_lobby_invite(self, invite_id: str, user_id: str) -> bool:
        """Accept a lobby invite"""
        query = "SELECT * FROM c WHERE c.id = @inviteId AND c.invitee_id = @userId"
        parameters = [
            {"name": "@inviteId", "value": invite_id},
            {"name": "@userId", "value": user_id}
        ]
        invites = self.db_service.query_items(self.db_service.lobbies_container, query, parameters)
        
        if not invites:
            return False
        
        invite = invites[0]
        
        # Check if invite is still valid
        if invite["expires_at"] < datetime.utcnow().isoformat():
            return False
        
        # Update invite status
        self.db_service.update_item(
            self.db_service.lobbies_container,
            invite_id,
            invite["lobby_id"],  # partition key
            {"is_accepted": True}
        )
        
        # Join the lobby
        return self.join_lobby(invite["lobby_id"], user_id)

    def decline_lobby_invite(self, invite_id: str, user_id: str) -> bool:
        """Decline a lobby invite"""
        query = "SELECT * FROM c WHERE c.id = @inviteId AND c.invitee_id = @userId"
        parameters = [
            {"name": "@inviteId", "value": invite_id},
            {"name": "@userId", "value": user_id}
        ]
        invites = self.db_service.query_items(self.db_service.lobbies_container, query, parameters)
        
        if not invites:
            return False
        
        invite = invites[0]
        
        # Update invite status
        self.db_service.update_item(
            self.db_service.lobbies_container,
            invite_id,
            invite["lobby_id"],  # partition key
            {"is_accepted": False}
        )
        
        return True 