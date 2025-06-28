import azure.functions as func
import logging
import json
from services.database import DatabaseService
from services.auth import AuthService
from services.user_service import UserService

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()
user_service = UserService(db_service, auth_service)

app = func.FunctionApp()

def get_current_user(req: func.HttpRequest):
    """Helper function to get current user from token"""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return auth_service.get_current_user(db_service, token)

def _get_user_profile_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get user profile by ID (testable logic)"""
    try:
        user_id = req.route_params.get("user_id")
        profile = user_service.get_user_profile(user_id)
        
        if not profile:
            return func.HttpResponse(
                json.dumps({"error": "User not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(profile.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get user profile error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="users", methods=["GET"])
def get_users(req: func.HttpRequest) -> func.HttpResponse:
    return _get_users_impl(req)

def _get_users_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Search users (testable logic)"""
    try:
        search = req.params.get("search")
        limit = int(req.params.get("limit", 10))
        
        if not search:
            return func.HttpResponse(
                json.dumps({"error": "search parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        users = user_service.search_users(search, limit)
        
        return func.HttpResponse(
            json.dumps([user.dict() for user in users]),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get users error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="users/{user_id}", methods=["GET"])
def get_user_profile(req: func.HttpRequest) -> func.HttpResponse:
    return _get_user_profile_impl(req)

@app.route(route="users/profile", methods=["PUT"])
def update_profile(req: func.HttpRequest) -> func.HttpResponse:
    return _update_profile_impl(req)

def _update_profile_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Update current user's profile (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        req_body = req.get_json()
        allowed_updates = ["display_name", "avatar_url"]
        updates = {k: v for k, v in req_body.items() if k in allowed_updates}
        
        if not updates:
            return func.HttpResponse(
                json.dumps({"error": "No valid fields to update"}),
                status_code=400,
                mimetype="application/json"
            )
        
        updated_user = user_service.update_user_profile(user.id, updates)
        
        if not updated_user:
            return func.HttpResponse(
                json.dumps({"error": "Failed to update profile"}),
                status_code=400,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(updated_user.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Update profile error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="users/me", methods=["GET"])
def get_my_profile(req: func.HttpRequest) -> func.HttpResponse:
    return _get_my_profile_impl(req)

def _get_my_profile_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get current user's profile (testable logic)"""
    try:
        user = get_current_user(req)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized"}),
                status_code=401,
                mimetype="application/json"
            )
        
        profile = user_service.get_user_profile(user.id)
        
        if not profile:
            return func.HttpResponse(
                json.dumps({"error": "Profile not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(profile.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get my profile error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        ) 