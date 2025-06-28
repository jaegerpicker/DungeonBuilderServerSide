import azure.functions as func
import logging
import json
from services.database import DatabaseService
from services.auth import AuthService
from services.guild_service import GuildService
from models.guild import GuildCreate

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()
guild_service = GuildService(db_service)

app = func.FunctionApp()

def get_current_user(req: func.HttpRequest):
    """Helper function to get current user from token"""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return auth_service.get_current_user(db_service, token)

def _create_guild_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new guild (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        req_body = req.get_json()
        guild_create = GuildCreate(**req_body)
        guild = guild_service.create_guild(guild_create, user.id)
        return func.HttpResponse(
            json.dumps(guild.dict()),
            status_code=201,
            mimetype="application/json"
        )
    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Create guild error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="guilds", methods=["POST"])
def create_guild(req: func.HttpRequest) -> func.HttpResponse:
    return _create_guild_impl(req)

@app.route(route="guilds", methods=["GET"])
def get_guilds(req: func.HttpRequest) -> func.HttpResponse:
    return _get_guilds_impl(req)

def _get_guilds_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get guilds with optional filtering (testable logic)"""
    try:
        search = req.params.get("search")
        leader_id = req.params.get("leader_id")
        limit = int(req.params.get("limit", 20))
        
        if search:
            guilds = guild_service.search_guilds(search, limit)
        elif leader_id:
            guilds = guild_service.get_guilds_by_leader(leader_id)
        else:
            guilds = guild_service.get_public_guilds(limit)
        
        return func.HttpResponse(
            json.dumps([guild.dict() for guild in guilds]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get guilds error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="guilds/{guild_id}", methods=["GET"])
def get_guild(req: func.HttpRequest) -> func.HttpResponse:
    return _get_guild_impl(req)

def _get_guild_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific guild by ID (testable logic)"""
    try:
        guild_id = req.route_params.get("guild_id")
        guild = guild_service.get_guild_by_id(guild_id)
        
        if not guild:
            return func.HttpResponse(
                json.dumps({"error": "Guild not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(guild.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get guild error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="guilds/{guild_id}/members", methods=["GET"])
def get_guild_members(req: func.HttpRequest) -> func.HttpResponse:
    return _get_guild_members_impl(req)

def _get_guild_members_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get guild members (testable logic)"""
    try:
        guild_id = req.route_params.get("guild_id")
        members = guild_service.get_guild_members(guild_id)
        
        return func.HttpResponse(
            json.dumps([member.dict() for member in members]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get guild members error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="guilds/{guild_id}/members", methods=["POST"])
def add_guild_member(req: func.HttpRequest) -> func.HttpResponse:
    return _add_guild_member_impl(req)

def _add_guild_member_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Add a member to a guild (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        guild_id = req.route_params.get("guild_id")
        req_body = req.get_json()
        member_id = req_body.get("user_id")
        role = req_body.get("role", "member")
        
        if not member_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        success = guild_service.add_member_to_guild(guild_id, member_id, role)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to add member to guild"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Member added successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Add guild member error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="guilds/{guild_id}/members/{member_id}", methods=["DELETE"])
def remove_guild_member(req: func.HttpRequest) -> func.HttpResponse:
    return _remove_guild_member_impl(req)

def _remove_guild_member_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Remove a member from a guild (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        guild_id = req.route_params.get("guild_id")
        member_id = req.route_params.get("member_id")
        
        success = guild_service.remove_member_from_guild(guild_id, member_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to remove member from guild"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Member removed successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Remove guild member error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="guilds/{guild_id}", methods=["PUT"])
def update_guild(req: func.HttpRequest) -> func.HttpResponse:
    return _update_guild_impl(req)

def _update_guild_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Update guild information (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        guild_id = req.route_params.get("guild_id")
        req_body = req.get_json()
        
        guild = guild_service.update_guild(guild_id, user.id, req_body)
        
        if not guild:
            return func.HttpResponse(
                json.dumps({"error": "Guild not found or unauthorized"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(guild.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Update guild error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="guilds/my", methods=["GET"])
def get_my_guild(req: func.HttpRequest) -> func.HttpResponse:
    return _get_my_guild_impl(req)

def _get_my_guild_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get the guild that the current user belongs to (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        guild = guild_service.get_user_guild(user.id)
        
        if not guild:
            return func.HttpResponse(
                json.dumps({"error": "User is not in a guild"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(guild.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get my guild error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        ) 