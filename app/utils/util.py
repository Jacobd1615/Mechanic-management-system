# Token utility functions will be defined here
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from functools import wraps
from flask import request, jsonify


SECRET_KEY = "your_secret_key_here"


def encode_token(user_id, role="customer"):
    """Generates a JWT token containing the user's ID and role."""
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
        "role": role,  # Add role to the payload
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def encode_mechanic_token(mechanic_id):
    """Generates a JWT token for a mechanic, including a role."""
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(mechanic_id),
        "role": "mechanic",  # Add role to the payload
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def token_require(f):
    """A decorator to protect routes, requiring a valid token for a customer or mechanic."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing. Please log in."}), 401

        try:
            # Decode the token to get the user's ID
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_role = payload.get("role")
            user_id = payload["sub"]
        except ExpiredSignatureError:
            return jsonify({"message": "Session expired. Please log in again."}), 401
        except JWTError:
            return jsonify({"message": "Invalid token. Please log in again."}), 401

        # Check if the role is either customer or mechanic
        if user_role not in ["customer", "mechanic"]:
            return jsonify({"message": "Invalid role. Access denied."}), 403

        # Pass the user_id to the decorated function as a keyword argument
        kwargs["user_id"] = user_id
        return f(*args, **kwargs)

    return decorated_function


# Verified and retained utility functions for mechanics and customers.
