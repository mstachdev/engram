from flask import jsonify
from typing import Dict, Any, Optional

def success_response(data: Dict[str, Any], message: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized success response."""
    response = {
        "success": True,
        "data": data
    }
    if message:
        response["message"] = message
    return jsonify(response)

def error_response(error: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> tuple:
    """Create a standardized error response."""
    response = {
        "success": False,
        "error": error
    }
    if details:
        response["details"] = details
    return jsonify(response), status_code

def validation_error(message: str, field: Optional[str] = None) -> tuple:
    """Create a validation error response."""
    details = {}
    if field:
        details["field"] = field
    return error_response(f"Validation error: {message}", 400, details)

def not_found_error(resource: str) -> tuple:
    """Create a not found error response."""
    return error_response(f"{resource} not found", 404)

def server_error(message: str = "Internal server error") -> tuple:
    """Create a server error response."""
    return error_response(message, 500)