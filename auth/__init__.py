import azure.functions as func
import logging
import json
from datetime import datetime
from services.database import DatabaseService
from services.auth import AuthService
from services.user_service import UserService
from models.user import UserCreate, UserLogin

# Initialize services
db_service = DatabaseService()
auth_service = AuthService()
user_service = UserService(db_service, auth_service)

app = func.FunctionApp()

def _register_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new user (testable logic)"""
    try:
        req_body = req.get_json()
        user_create = UserCreate(**req_body)
        user = user_service.create_user(user_create)
        # Create access token
        access_token = auth_service.create_access_token(data={"sub": user.username})
        return func.HttpResponse(
            json.dumps({
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.display_name
                }
            }),
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
        logging.error(f"Registration error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="auth/register", methods=["POST"])
def register(req: func.HttpRequest) -> func.HttpResponse:
    return _register_impl(req)

def _login_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Login user (testable logic)"""
    try:
        req_body = req.get_json()
        user_login = UserLogin(**req_body)
        user = auth_service.authenticate_user(db_service, user_login.username, user_login.password)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Invalid credentials"}),
                status_code=401,
                mimetype="application/json"
            )
        # Update last login
        user_service.update_last_login(user.id)
        # Create access token
        access_token = auth_service.create_access_token(data={"sub": user.username})
        return func.HttpResponse(
            json.dumps({
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.display_name
                }
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="auth/login", methods=["POST"])
def login(req: func.HttpRequest) -> func.HttpResponse:
    return _login_impl(req)

def _get_current_user_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Get current user profile (testable logic)"""
    try:
        # Get token from Authorization header
        auth_header = req.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return func.HttpResponse(
                json.dumps({"error": "Missing or invalid authorization header"}),
                status_code=401,
                mimetype="application/json"
            )
        token = auth_header.split(" ")[1]
        user = auth_service.get_current_user(db_service, token)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "Invalid token"}),
                status_code=401,
                mimetype="application/json"
            )
        user_profile = user_service.get_user_profile(user.id)
        return func.HttpResponse(
            json.dumps(user_profile.dict()),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get current user error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="auth/me", methods=["GET"])
def get_current_user(req: func.HttpRequest) -> func.HttpResponse:
    return _get_current_user_impl(req) 