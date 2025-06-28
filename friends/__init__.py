import azure.functions as func
import logging
import json
from services.database import DatabaseService
from services.auth import AuthService
from services.friendship_service import FriendshipService
from models.friendship import FriendshipRequest

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()
friendship_service = FriendshipService(db_service)

app = func.FunctionApp()

def get_current_user(req: func.HttpRequest):
    """Helper function to get current user from token"""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return auth_service.get_current_user(db_service, token)

def _send_friend_request_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Send a friend request (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        req_body = req.get_json()
        friendship_request = FriendshipRequest(**req_body)
        friendship = friendship_service.send_friend_request(user.id, friendship_request.addressee_id)
        return func.HttpResponse(
            json.dumps(friendship.dict()),
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
        logging.error(f"Send friend request error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/request", methods=["POST"])
def send_friend_request(req: func.HttpRequest) -> func.HttpResponse:
    return _send_friend_request_impl(req)

@app.route(route="friends/request/{requester_id}/accept", methods=["POST"])
def accept_friend_request(req: func.HttpRequest) -> func.HttpResponse:
    return _accept_friend_request_impl(req)

def _accept_friend_request_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Accept a friend request (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        requester_id = req.route_params.get("requester_id")
        success = friendship_service.accept_friend_request(user.id, requester_id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to accept friend request"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Friend request accepted successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Accept friend request error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/request/{requester_id}/reject", methods=["POST"])
def reject_friend_request(req: func.HttpRequest) -> func.HttpResponse:
    return _reject_friend_request_impl(req)

def _reject_friend_request_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Reject a friend request (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        requester_id = req.route_params.get("requester_id")
        success = friendship_service.reject_friend_request(user.id, requester_id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to reject friend request"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Friend request rejected successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Reject friend request error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends", methods=["GET"])
def get_friends(req: func.HttpRequest) -> func.HttpResponse:
    return _get_friends_impl(req)

def _get_friends_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of friends (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        friend_ids = friendship_service.get_friends(user.id)
        
        return func.HttpResponse(
            json.dumps({"friends": friend_ids}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get friends error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/requests/pending", methods=["GET"])
def get_pending_requests(req: func.HttpRequest) -> func.HttpResponse:
    return _get_pending_requests_impl(req)

def _get_pending_requests_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get pending friend requests (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        requests = friendship_service.get_pending_requests(user.id)
        
        return func.HttpResponse(
            json.dumps([req.dict() for req in requests]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get pending requests error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/requests/sent", methods=["GET"])
def get_sent_requests(req: func.HttpRequest) -> func.HttpResponse:
    return _get_sent_requests_impl(req)

def _get_sent_requests_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get sent friend requests (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        requests = friendship_service.get_sent_requests(user.id)
        
        return func.HttpResponse(
            json.dumps([req.dict() for req in requests]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get sent requests error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/{friend_id}", methods=["DELETE"])
def remove_friend(req: func.HttpRequest) -> func.HttpResponse:
    return _remove_friend_impl(req)

def _remove_friend_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Remove a friend (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        friend_id = req.route_params.get("friend_id")
        success = friendship_service.remove_friend(user.id, friend_id)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to remove friend"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "Friend removed successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Remove friend error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/{user_id}/block", methods=["POST"])
def block_user(req: func.HttpRequest) -> func.HttpResponse:
    return _block_user_impl(req)

def _block_user_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Block a user (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        user_id_to_block = req.route_params.get("user_id")
        friendship = friendship_service.block_user(user.id, user_id_to_block)
        
        return func.HttpResponse(
            json.dumps(friendship.dict()),
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
        logging.error(f"Block user error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/{user_id}/unblock", methods=["POST"])
def unblock_user(req: func.HttpRequest) -> func.HttpResponse:
    return _unblock_user_impl(req)

def _unblock_user_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Unblock a user (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        user_id_to_unblock = req.route_params.get("user_id")
        success = friendship_service.unblock_user(user.id, user_id_to_unblock)
        
        if not success:
            return func.HttpResponse(
                json.dumps({"error": "Failed to unblock user"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps({"message": "User unblocked successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unblock user error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="friends/{user_id}/check", methods=["GET"])
def check_friendship(req: func.HttpRequest) -> func.HttpResponse:
    return _check_friendship_impl(req)

def _check_friendship_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Check friendship status with a user (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        other_user_id = req.route_params.get("user_id")
        are_friends = friendship_service.are_friends(user.id, other_user_id)
        is_blocked = friendship_service.is_blocked(user.id, other_user_id)
        
        return func.HttpResponse(
            json.dumps({
                "are_friends": are_friends,
                "is_blocked": is_blocked
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Check friendship error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        ) 