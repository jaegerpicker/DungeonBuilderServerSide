import azure.functions as func
import json
from datetime import datetime

app = func.FunctionApp()

def _health_check_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for the API (testable logic)"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Dungeon Builder Backend",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth",
                "users": "/api/users",
                "dungeons": "/api/dungeons",
                "guilds": "/api/guilds",
                "lobbies": "/api/lobbies",
                "friends": "/api/friends",
                "leaderboard": "/api/leaderboard"
            }
        }
        return func.HttpResponse(
            json.dumps(health_data),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        error_data = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
        return func.HttpResponse(
            json.dumps(error_data),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return _health_check_impl(req) 