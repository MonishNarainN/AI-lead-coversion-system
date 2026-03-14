import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.environ.get('JWT_SECRET', 'leadpro-super-secret-key-change-in-production')

# Demo user store (replace with database in production)
DEMO_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "analyst": {"password": "analyst123", "role": "analyst"},
    "viewer": {"password": "viewer123", "role": "viewer"},
}


def generate_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


def require_auth(f):
    """Decorator: require a valid JWT Bearer token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token required", "code": 401}), 401
        token = auth_header.split(' ', 1)[1]
        try:
            payload = decode_token(token)
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired", "code": 401}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token", "code": 401}), 401
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorator: require one of the listed roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, 'current_user', {})
            if user.get('role') not in roles:
                return jsonify({"error": "Insufficient permissions", "code": 403}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
