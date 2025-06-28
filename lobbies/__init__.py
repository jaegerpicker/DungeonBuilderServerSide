import azure.functions as func
import logging
import json
from services.database import DatabaseService
from services.auth import AuthService
from services.lobby_service import LobbyService
from models.lobby import LobbyCreate

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()
lobby_service = LobbyService(db_service)

app = func.FunctionApp()

def get_current_user(req: func.HttpRequest):
    """Helper function to get current user from token"""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return auth_service.get_current_user(db_service, token)

def _create_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new lobby (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        req_body = req.get_json()
        lobby_create = LobbyCreate(**req_body)
        lobby = lobby_service.create_lobby(lobby_create, user.id)
        return func.HttpResponse(
            json.dumps(lobby.dict()),
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
        logging.error(f"Create lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies", methods=["POST"])
def create_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _create_lobby_impl(req)

@app.route(route="lobbies", methods=["GET"])
def get_lobbies(req: func.HttpRequest) -> func.HttpResponse:
    return _get_lobbies_impl(req)

def _get_lobbies_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get lobbies with optional filtering (testable logic)"""
    try:
        creator_id = req.params.get("creator_id")
        limit = int(req.params.get("limit", 20))
        
        if creator_id:
            lobbies = lobby_service.get_lobbies_by_creator(creator_id)
        else:
            lobbies = lobby_service.get_public_lobbies(limit)
        
        return func.HttpResponse(
            json.dumps([lobby.dict() for lobby in lobbies]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get lobbies error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/{lobby_id}", methods=["GET"])
def get_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _get_lobby_impl(req)

def _get_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific lobby by ID (testable logic)"""
    try:
        lobby_id = req.route_params.get("lobby_id")
        lobby = lobby_service.get_lobby_by_id(lobby_id)
        
        if not lobby:
            return func.HttpResponse(
                json.dumps({"error": "Lobby not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(lobby.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/{lobby_id}/join", methods=["POST"])
def join_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _join_lobby_impl(req)

def _join_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Join a lobby (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        lobby_id = req.route_params.get("lobby_id")
        req_body = req.get_json() or {}
        password = req_body.get("password")
        
        success = lobby_service.join_lobby(lobby_id, user.id, password)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to join lobby"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Successfully joined lobby"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Join lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/{lobby_id}/leave", methods=["POST"])
def leave_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _leave_lobby_impl(req)

def _leave_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Leave a lobby (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        lobby_id = req.route_params.get("lobby_id")
        success = lobby_service.leave_lobby(lobby_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to leave lobby"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Successfully left lobby"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Leave lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/{lobby_id}/start", methods=["POST"])
def start_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _start_lobby_impl(req)

def _start_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Start a lobby (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        lobby_id = req.route_params.get("lobby_id")
        success = lobby_service.start_lobby(lobby_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to start lobby"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Lobby started successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Start lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/{lobby_id}/complete", methods=["POST"])
def complete_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _complete_lobby_impl(req)

def _complete_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Complete a lobby (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        lobby_id = req.route_params.get("lobby_id")
        success = lobby_service.complete_lobby(lobby_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to complete lobby"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Lobby completed successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Complete lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/{lobby_id}/cancel", methods=["POST"])
def cancel_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _cancel_lobby_impl(req)

def _cancel_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Cancel a lobby (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        lobby_id = req.route_params.get("lobby_id")
        success = lobby_service.cancel_lobby(lobby_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to cancel lobby"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Lobby cancelled successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Cancel lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/{lobby_id}/invite", methods=["POST"])
def invite_to_lobby(req: func.HttpRequest) -> func.HttpResponse:
    return _invite_to_lobby_impl(req)

def _invite_to_lobby_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Invite a user to a lobby (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        lobby_id = req.route_params.get("lobby_id")
        req_body = req.get_json()
        invitee_id = req_body.get("user_id")
        
        if not invitee_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        lobby_invite = lobby_service.create_lobby_invite(lobby_id, user.id, invitee_id)
        
        return func.HttpResponse(
            json.dumps(lobby_invite.dict()),
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
        logging.error(f"Invite to lobby error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/invites", methods=["GET"])
def get_lobby_invites(req: func.HttpRequest) -> func.HttpResponse:
    return _get_lobby_invites_impl(req)

def _get_lobby_invites_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get lobby invites for current user (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        invites = lobby_service.get_lobby_invites(user.id)
        
        return func.HttpResponse(
            json.dumps([invite.dict() for invite in invites]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get lobby invites error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/invites/{invite_id}/accept", methods=["POST"])
def accept_lobby_invite(req: func.HttpRequest) -> func.HttpResponse:
    return _accept_lobby_invite_impl(req)

def _accept_lobby_invite_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Accept a lobby invite (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        invite_id = req.route_params.get("invite_id")
        success = lobby_service.accept_lobby_invite(invite_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to accept invite"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Invite accepted successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Accept lobby invite error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="lobbies/invites/{invite_id}/decline", methods=["POST"])
def decline_lobby_invite(req: func.HttpRequest) -> func.HttpResponse:
    return _decline_lobby_invite_impl(req)

def _decline_lobby_invite_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Decline a lobby invite (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        invite_id = req.route_params.get("invite_id")
        success = lobby_service.decline_lobby_invite(invite_id, user.id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to decline invite"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Invite declined successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Decline lobby invite error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        ) 