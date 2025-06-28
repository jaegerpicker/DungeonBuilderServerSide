import azure.functions as func
import logging
import json
from services.database import DatabaseService
from services.auth import AuthService
from services.leaderboard_service import LeaderboardService

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()
leaderboard_service = LeaderboardService(db_service)

app = func.FunctionApp()

def get_current_user(req: func.HttpRequest):
    """Helper function to get current user from token"""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return auth_service.get_current_user(db_service, token)

def _get_player_leaderboard_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get player leaderboard (testable logic)"""
    try:
        limit = int(req.params.get("limit", 50))
        players = leaderboard_service.get_player_leaderboard(limit)
        return func.HttpResponse(
            json.dumps([player.dict() for player in players]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get player leaderboard error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/players", methods=["GET"])
def get_player_leaderboard(req: func.HttpRequest) -> func.HttpResponse:
    return _get_player_leaderboard_impl(req)

@app.route(route="leaderboard/dungeons", methods=["GET"])
def get_dungeon_leaderboard(req: func.HttpRequest) -> func.HttpResponse:
    return _get_dungeon_leaderboard_impl(req)

def _get_dungeon_leaderboard_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get dungeon leaderboard (testable logic)"""
    try:
        limit = int(req.params.get("limit", 50))
        dungeons = leaderboard_service.get_dungeon_leaderboard(limit)
        
        return func.HttpResponse(
            json.dumps([dungeon.dict() for dungeon in dungeons]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get dungeon leaderboard error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/players/rank/{user_id}", methods=["GET"])
def get_player_rank(req: func.HttpRequest) -> func.HttpResponse:
    return _get_player_rank_impl(req)

def _get_player_rank_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get player's rank in leaderboard (testable logic)"""
    try:
        user_id = req.route_params.get("user_id")
        rank = leaderboard_service.get_player_rank(user_id)
        
        if rank is None:
            return func.HttpResponse(
                json.dumps({"error": "Player not found in leaderboard"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"rank": rank}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get player rank error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/dungeons/rank/{dungeon_id}", methods=["GET"])
def get_dungeon_rank(req: func.HttpRequest) -> func.HttpResponse:
    return _get_dungeon_rank_impl(req)

def _get_dungeon_rank_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get dungeon's rank in leaderboard (testable logic)"""
    try:
        dungeon_id = req.route_params.get("dungeon_id")
        rank = leaderboard_service.get_dungeon_rank(dungeon_id)
        
        if rank is None:
            return func.HttpResponse(
                json.dumps({"error": "Dungeon not found in leaderboard"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"rank": rank}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get dungeon rank error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/players/{user_id}", methods=["GET"])
def get_player_score(req: func.HttpRequest) -> func.HttpResponse:
    return _get_player_score_impl(req)

def _get_player_score_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get player's score (testable logic)"""
    try:
        user_id = req.route_params.get("user_id")
        score = leaderboard_service.get_player_score(user_id)
        
        if not score:
            return func.HttpResponse(
                json.dumps({"error": "Player score not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(score.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get player score error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/dungeons/{dungeon_id}", methods=["GET"])
def get_dungeon_score(req: func.HttpRequest) -> func.HttpResponse:
    return _get_dungeon_score_impl(req)

def _get_dungeon_score_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get dungeon's score (testable logic)"""
    try:
        dungeon_id = req.route_params.get("dungeon_id")
        score = leaderboard_service.get_dungeon_score(dungeon_id)
        
        if not score:
            return func.HttpResponse(
                json.dumps({"error": "Dungeon score not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(score.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get dungeon score error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/players/top-creators", methods=["GET"])
def get_top_creators(req: func.HttpRequest) -> func.HttpResponse:
    return _get_top_creators_impl(req)

def _get_top_creators_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get top dungeon creators (testable logic)"""
    try:
        limit = int(req.params.get("limit", 20))
        creators = leaderboard_service.get_top_creators(limit)
        
        return func.HttpResponse(
            json.dumps([creator.dict() for creator in creators]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get top creators error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/dungeons/most-played", methods=["GET"])
def get_most_played_dungeons(req: func.HttpRequest) -> func.HttpResponse:
    return _get_most_played_dungeons_impl(req)

def _get_most_played_dungeons_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get most played dungeons (testable logic)"""
    try:
        limit = int(req.params.get("limit", 20))
        dungeons = leaderboard_service.get_most_played_dungeons(limit)
        
        return func.HttpResponse(
            json.dumps([dungeon.dict() for dungeon in dungeons]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get most played dungeons error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/players/update", methods=["POST"])
def update_player_score(req: func.HttpRequest) -> func.HttpResponse:
    return _update_player_score_impl(req)

def _update_player_score_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Update player score (admin only) (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        req_body = req.get_json()
        user_id = req_body.get("user_id")
        username = req_body.get("username")
        score = req_body.get("score", 0)
        dungeons_completed = req_body.get("dungeons_completed", 0)
        dungeons_created = req_body.get("dungeons_created", 0)
        average_rating = req_body.get("average_rating", 0.0)
        
        if not user_id or not username:
            return func.HttpResponse(
                json.dumps({"error": "user_id and username are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        leaderboard_service.update_player_score(
            user_id, username, score, dungeons_completed, dungeons_created, average_rating
        )
        
        return func.HttpResponse(
            json.dumps({"message": "Player score updated successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Update player score error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="leaderboard/dungeons/update", methods=["POST"])
def update_dungeon_score(req: func.HttpRequest) -> func.HttpResponse:
    return _update_dungeon_score_impl(req)

def _update_dungeon_score_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Update dungeon score (admin only) (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        req_body = req.get_json()
        dungeon_id = req_body.get("dungeon_id")
        dungeon_name = req_body.get("dungeon_name")
        creator_username = req_body.get("creator_username")
        score = req_body.get("score", 0)
        play_count = req_body.get("play_count", 0)
        average_rating = req_body.get("average_rating", 0.0)
        total_ratings = req_body.get("total_ratings", 0)
        
        if not dungeon_id or not dungeon_name or not creator_username:
            return func.HttpResponse(
                json.dumps({"error": "dungeon_id, dungeon_name, and creator_username are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        leaderboard_service.update_dungeon_score(
            dungeon_id, dungeon_name, creator_username, score, play_count, average_rating, total_ratings
        )
        
        return func.HttpResponse(
            json.dumps({"message": "Dungeon score updated successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Update dungeon score error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        ) 