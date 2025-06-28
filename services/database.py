import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

class DatabaseService:
    def __init__(self):
        endpoint = os.environ.get("COSMOS_DB_ENDPOINT")
        key = os.environ.get("COSMOS_DB_KEY")
        database_name = os.environ.get("COSMOS_DB_DATABASE", "DungeonBuilderDB")
        
        self.client = CosmosClient(endpoint, key)
        self.database = self.client.get_database_client(database_name)
        
        # Initialize containers
        self.users_container = self.database.get_container_client("users")
        self.dungeons_container = self.database.get_container_client("dungeons")
        self.guilds_container = self.database.get_container_client("guilds")
        self.lobbies_container = self.database.get_container_client("lobbies")
        self.friendships_container = self.database.get_container_client("friendships")
        self.ratings_container = self.database.get_container_client("ratings")
        self.leaderboard_container = self.database.get_container_client("leaderboard")

    def create_item(self, container, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in the specified container"""
        item['id'] = str(uuid.uuid4())
        item['created_at'] = datetime.utcnow().isoformat()
        item['updated_at'] = datetime.utcnow().isoformat()
        return container.create_item(item)

    def get_item(self, container, item_id: str, partition_key: str) -> Optional[Dict[str, Any]]:
        """Get an item by ID and partition key"""
        try:
            return container.read_item(item_id, partition_key)
        except CosmosResourceNotFoundError:
            return None

    def update_item(self, container, item_id: str, partition_key: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing item"""
        item = self.get_item(container, item_id, partition_key)
        if not item:
            raise ValueError(f"Item {item_id} not found")
        
        item.update(updates)
        item['updated_at'] = datetime.utcnow().isoformat()
        return container.replace_item(item_id, item)

    def delete_item(self, container, item_id: str, partition_key: str) -> bool:
        """Delete an item by ID and partition key"""
        try:
            container.delete_item(item_id, partition_key)
            return True
        except CosmosResourceNotFoundError:
            return False

    def query_items(self, container, query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Query items using SQL query"""
        if parameters:
            return list(container.query_items(query, parameters=parameters))
        return list(container.query_items(query))

    def get_items_by_partition(self, container, partition_key: str) -> List[Dict[str, Any]]:
        """Get all items for a specific partition key"""
        query = "SELECT * FROM c WHERE c.partitionKey = @partitionKey"
        parameters = [{"name": "@partitionKey", "value": partition_key}]
        return self.query_items(container, query, parameters) 