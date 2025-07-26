from functools import wraps
from flask import request, jsonify
from jose import jwt, ExpiredSignatureError, JWTError
from app.models import Customer, Mechanic, db
from .util import SECRET_KEY


def _token_required(role_names, model):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get("Authorization")

            # Debugging: Log the raw Authorization header
            print(f"Raw Authorization Header: {auth_header}")

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            else:
                # Reject cases where the prefix is missing
                return (
                    jsonify(
                        {"message": "Authorization header must start with 'Bearer '."}
                    ),
                    401,
                )

            # Debugging: Log the extracted token
            print(f"Extracted Token: {token}")

            if not token:
                print("Token is missing after parsing.")  # Debugging
                return jsonify({"message": "Token is missing. Please log in."}), 401

            try:
                # Debugging: Log the SECRET_KEY being used
                print(f"SECRET_KEY: {SECRET_KEY}")

                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

                # Debugging: Log the decoded token payload
                print(f"Decoded Token Payload: {payload}")

                # Allow for a list of roles
                allowed_roles = (
                    role_names if isinstance(role_names, list) else [role_names]
                )

                # Debugging: Log the expected roles
                print(f"Expected Roles: {allowed_roles}")

                user_role = payload.get("role")

                # Debugging: Log the user role from the token
                print(f"User Role from Token: {user_role}")

                if user_role not in allowed_roles:
                    print(
                        f"Access denied. User role '{user_role}' not in {allowed_roles}"
                    )  # Debugging
                    return (
                        jsonify(
                            {
                                "message": f"Access denied. Required roles: {allowed_roles}"
                            }
                        ),
                        403,
                    )

                user_id = payload["sub"]
                current_user = db.session.get(model, int(user_id))

                # Debugging: Log the current user fetched from the database
                print(f"Current User: {current_user}")

                if not current_user:
                    print(f"User ID {user_id} not found in the database.")  # Debugging
                    return (
                        jsonify(
                            {
                                "message": f"Invalid token: {user_role} with ID {user_id} not found. Please log in again."
                            }
                        ),
                        401,
                    )

            except ExpiredSignatureError:
                print("Token has expired.")  # Debugging
                return (
                    jsonify({"message": "Session expired. Please log in again."}),
                    401,
                )
            except JWTError as e:
                print(f"Invalid token. Error: {e}")  # Debugging
                return jsonify({"message": "Invalid token. Please log in again."}), 401

            return f(current_user, *args, **kwargs)

        return decorated_function

    return decorator


mechanic_token_required = _token_required("mechanic", Mechanic)
customer_token_required = _token_required("customer", Customer)

# Verified and retained role-based access control for mechanics and customers.
