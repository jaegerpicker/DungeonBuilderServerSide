import azure.functions as func
import logging
import json
from services.database import DatabaseService
from services.auth import AuthService
from services.dungeon_service import DungeonService
from models.dungeon import DungeonCreate

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()
dungeon_service = DungeonService(db_service)

app = func.FunctionApp()

def get_current_user(req: func.HttpRequest):
    """Helper function to get current user from token"""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return auth_service.get_current_user(db_service, token)

def _create_dungeon_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new dungeon (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        req_body = req.get_json()
        dungeon_create = DungeonCreate(**req_body)
        dungeon = dungeon_service.create_dungeon(dungeon_create, user.id)
        return func.HttpResponse(
            json.dumps(dungeon.dict()),
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
        logging.error(f"Create dungeon error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="dungeons", methods=["POST"])
def create_dungeon(req: func.HttpRequest) -> func.HttpResponse:
    return _create_dungeon_impl(req)

@app.route(route="dungeons", methods=["GET"])
def get_dungeons(req: func.HttpRequest) -> func.HttpResponse:
    return _get_dungeons_impl(req)

def _get_dungeons_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get dungeons with optional filtering (testable logic)"""
    try:
        # Get query parameters
        limit = int(req.params.get("limit", 20))
        offset = int(req.params.get("offset", 0))
        difficulty = req.params.get("difficulty")
        search = req.params.get("search")
        creator_id = req.params.get("creator_id")
        
        if search:
            dungeons = dungeon_service.search_dungeons(search, limit)
        elif creator_id:
            dungeons = dungeon_service.get_dungeons_by_creator(creator_id, limit)
        else:
            dungeons = dungeon_service.get_public_dungeons(limit, offset, difficulty)
        
        return func.HttpResponse(
            json.dumps([dungeon.dict() for dungeon in dungeons]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get dungeons error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="dungeons/{dungeon_id}", methods=["GET"])
def get_dungeon(req: func.HttpRequest) -> func.HttpResponse:
    return _get_dungeon_impl(req)

def _get_dungeon_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific dungeon by ID (testable logic)"""
    try:
        dungeon_id = req.route_params.get("dungeon_id")
        dungeon = dungeon_service.get_dungeon_by_id(dungeon_id)
        
        if not dungeon:
            return func.HttpResponse(
                json.dumps({"error": "Dungeon not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(dungeon.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get dungeon error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="dungeons/{dungeon_id}", methods=["PUT"])
def update_dungeon(req: func.HttpRequest) -> func.HttpResponse:
    return _update_dungeon_impl(req)

def _update_dungeon_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Update a dungeon (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        dungeon_id = req.route_params.get("dungeon_id")
        req_body = req.get_json()
        
        dungeon = dungeon_service.update_dungeon(dungeon_id, user.id, req_body)
        
        if not dungeon:
            return func.HttpResponse(
                json.dumps({"error": "Dungeon not found or unauthorized"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(dungeon.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Update dungeon error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="dungeons/{dungeon_id}", methods=["DELETE"])
def delete_dungeon(req: func.HttpRequest) -> func.HttpResponse:
    return _delete_dungeon_impl(req)

def _delete_dungeon_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a dungeon (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        dungeon_id = req.route_params.get("dungeon_id")
        success = dungeon_service.delete_dungeon(dungeon_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Dungeon not found or unauthorized"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Dungeon deleted successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Delete dungeon error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="dungeons/{dungeon_id}/rate", methods=["POST"])
def rate_dungeon(req: func.HttpRequest) -> func.HttpResponse:
    return _rate_dungeon_impl(req)

def _rate_dungeon_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Rate a dungeon (1-5 stars) (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        dungeon_id = req.route_params.get("dungeon_id")
        req_body = req.get_json()
        
        rating = req_body.get("rating")
        comment = req_body.get("comment")
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return func.HttpResponse(
                json.dumps({"error": "Rating must be an integer between 1 and 5"}),
                status_code=400,
                mimetype="application/json"
            )
        
        dungeon_rating = dungeon_service.rate_dungeon(dungeon_id, user.id, rating, comment)
        
        return func.HttpResponse(
            json.dumps(dungeon_rating.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Rate dungeon error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="dungeons/{dungeon_id}/play", methods=["POST"])
def play_dungeon(req: func.HttpRequest) -> func.HttpResponse:
    return _play_dungeon_impl(req)

def _play_dungeon_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Increment dungeon play count (testable logic)"""
    try:
        dungeon_id = req.route_params.get("dungeon_id")
        dungeon_service.increment_play_count(dungeon_id)
        
        return func.HttpResponse(
            json.dumps({"message": "Play count incremented"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Play dungeon error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        ) 