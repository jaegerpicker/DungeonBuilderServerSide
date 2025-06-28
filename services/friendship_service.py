from datetime import datetime
from typing import List, Optional
from models.friendship import Friendship, FriendshipRequest
from services.database import DatabaseService

class FriendshipService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def send_friend_request(self, requester_id: str, addressee_id: str) -> Friendship:
        """Send a friend request"""
        if requester_id == addressee_id:
            raise ValueError("Cannot send friend request to yourself")
        
        # Check if friendship already exists
        existing_friendship = self._get_friendship(requester_id, addressee_id)
        if existing_friendship:
            raise ValueError("Friendship request already exists")
        
        friendship_data = {
            "requester_id": requester_id,
            "addressee_id": addressee_id,
            "status": "pending",
            "partitionKey": requester_id
        }
        
        created_friendship = self.db_service.create_item(self.db_service.friendships_container, friendship_data)
        return Friendship(**created_friendship)

    def accept_friend_request(self, addressee_id: str, requester_id: str) -> bool:
        """Accept a friend request"""
        friendship = self._get_friendship(requester_id, addressee_id)
        if not friendship or friendship.status != "pending":
            return False
        
        # Update friendship status
        self.db_service.update_item(
            self.db_service.friendships_container,
            friendship.id,
            requester_id,  # partition key
            {"status": "accepted"}
        )
        
        return True

    def reject_friend_request(self, addressee_id: str, requester_id: str) -> bool:
        """Reject a friend request"""
        friendship = self._get_friendship(requester_id, addressee_id)
        if not friendship or friendship.status != "pending":
            return False
        
        # Update friendship status
        self.db_service.update_item(
            self.db_service.friendships_container,
            friendship.id,
            requester_id,  # partition key
            {"status": "rejected"}
        )
        
        return True

    def block_user(self, blocker_id: str, blocked_id: str) -> Friendship:
        """Block a user"""
        if blocker_id == blocked_id:
            raise ValueError("Cannot block yourself")
        
        # Check if friendship already exists
        existing_friendship = self._get_friendship(blocker_id, blocked_id)
        if existing_friendship:
            # Update existing friendship
            updated_friendship = self.db_service.update_item(
                self.db_service.friendships_container,
                existing_friendship.id,
                blocker_id,  # partition key
                {"status": "blocked"}
            )
            return Friendship(**updated_friendship)
        else:
            # Create new blocked friendship
            friendship_data = {
                "requester_id": blocker_id,
                "addressee_id": blocked_id,
                "status": "blocked",
                "partitionKey": blocker_id
            }
            created_friendship = self.db_service.create_item(self.db_service.friendships_container, friendship_data)
            return Friendship(**created_friendship)

    def unblock_user(self, blocker_id: str, blocked_id: str) -> bool:
        """Unblock a user"""
        friendship = self._get_friendship(blocker_id, blocked_id)
        if not friendship or friendship.status != "blocked":
            return False
        
        # Delete the friendship
        return self.db_service.delete_item(
            self.db_service.friendships_container,
            friendship.id,
            blocker_id  # partition key
        )

    def remove_friend(self, user_id: str, friend_id: str) -> bool:
        """Remove a friend"""
        friendship = self._get_friendship(user_id, friend_id)
        if not friendship or friendship.status != "accepted":
            return False
        
        # Delete the friendship
        return self.db_service.delete_item(
            self.db_service.friendships_container,
            friendship.id,
            user_id  # partition key
        )

    def get_friends(self, user_id: str) -> List[str]:
        """Get list of friend IDs for a user"""
        # Get friendships where user is requester and status is accepted
        query = "SELECT * FROM c WHERE c.requester_id = @userId AND c.status = 'accepted'"
        parameters = [{"name": "@userId", "value": user_id}]
        friendships = self.db_service.query_items(self.db_service.friendships_container, query, parameters)
        
        # Get friendships where user is addressee and status is accepted
        query = "SELECT * FROM c WHERE c.addressee_id = @userId AND c.status = 'accepted'"
        parameters = [{"name": "@userId", "value": user_id}]
        friendships.extend(self.db_service.query_items(self.db_service.friendships_container, query, parameters))
        
        friend_ids = []
        for friendship in friendships:
            if friendship["requester_id"] == user_id:
                friend_ids.append(friendship["addressee_id"])
            else:
                friend_ids.append(friendship["requester_id"])
        
        return friend_ids

    def get_pending_requests(self, user_id: str) -> List[Friendship]:
        """Get pending friend requests for a user"""
        query = "SELECT * FROM c WHERE c.addressee_id = @userId AND c.status = 'pending'"
        parameters = [{"name": "@userId", "value": user_id}]
        friendships = self.db_service.query_items(self.db_service.friendships_container, query, parameters)
        
        return [Friendship(**friendship) for friendship in friendships]

    def get_sent_requests(self, user_id: str) -> List[Friendship]:
        """Get sent friend requests by a user"""
        query = "SELECT * FROM c WHERE c.requester_id = @userId AND c.status = 'pending'"
        parameters = [{"name": "@userId", "value": user_id}]
        friendships = self.db_service.query_items(self.db_service.friendships_container, query, parameters)
        
        return [Friendship(**friendship) for friendship in friendships]

    def are_friends(self, user_id: str, friend_id: str) -> bool:
        """Check if two users are friends"""
        friendship = self._get_friendship(user_id, friend_id)
        return friendship is not None and friendship.status == "accepted"

    def is_blocked(self, user_id: str, blocked_id: str) -> bool:
        """Check if a user is blocked by another user"""
        friendship = self._get_friendship(user_id, blocked_id)
        return friendship is not None and friendship.status == "blocked"

    def _get_friendship(self, user1_id: str, user2_id: str) -> Optional[Friendship]:
        """Get friendship between two users"""
        # Check both directions
        query = "SELECT * FROM c WHERE c.requester_id = @user1 AND c.addressee_id = @user2"
        parameters = [
            {"name": "@user1", "value": user1_id},
            {"name": "@user2", "value": user2_id}
        ]
        friendships = self.db_service.query_items(self.db_service.friendships_container, query, parameters)
        
        if friendships:
            return Friendship(**friendships[0])
        
        query = "SELECT * FROM c WHERE c.requester_id = @user2 AND c.addressee_id = @user1"
        parameters = [
            {"name": "@user2", "value": user2_id},
            {"name": "@user1", "value": user1_id}
        ]
        friendships = self.db_service.query_items(self.db_service.friendships_container, query, parameters)
        
        if friendships:
            return Friendship(**friendships[0])
        
        return None 