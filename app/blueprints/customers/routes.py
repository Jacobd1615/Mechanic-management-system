# Customer routes will be defined here
from .schemas import (
    customer_schema,
    customers_schema,
    login_schema,
    customer_update_schema,
)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token
from app.utils.roles import customer_token_required


@customers_bp.route("/login", methods=["POST"])
@limiter.limit("5/minute")  # Add rate limit to prevent brute-force attacks
def login():
    try:
        if request.json is None:
            return jsonify({"messages": "No JSON data provided"}), 400
        # Validate the request data using the login_schema
        credentials = login_schema.load(request.json)
        email = credentials["email"]
        password = credentials["password"]
    except ValidationError as e:
        return jsonify({"messages": e.messages}), 400

    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalar_one_or_none()

    if customer and customer.password == password:
        auth_token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token,
        }
        print(" welcome back, " + customer.name + "!")
        return jsonify(response), 200
    else:
        return jsonify({"messages": "Invalid email or password"}), 401


# creating new customer
@customers_bp.route("/", methods=["POST"])
@limiter.limit("10/hour")  # Rate limit: 10 requests per hour per IP
def create_customer():
    try:
        if request.json is None:
            return jsonify({"error": "No JSON data provided"}), 400
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return {"Error": e.messages}, 400

    query = select(Customer).where(Customer.email == customer_data.email)
    if db.session.execute(query).scalar_one_or_none():
        return jsonify({"Error": "Customer with this email already exists"}), 400

    password = request.json.get("password")
    if not password:
        return jsonify({"Error": "Password is required."}), 400

    new_customer = Customer(
        name=customer_data.name,
        email=customer_data.email,
        phone=customer_data.phone,
        password=password,
    )

    db.session.add(new_customer)
    db.session.commit()
    print("New customer created successfully.")
    return customer_schema.jsonify(new_customer), 201


# Route to get all customers
@customers_bp.route("/", methods=["GET"])
@customer_token_required
def get_all_customers(current_user):
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers)
    except (TypeError, ValueError):
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers), 200


# Route to get a customer by id
@customers_bp.route("/<int:customer_id>", methods=["GET"])
@customer_token_required
@cache.cached(timeout=60)
def find_customer(current_user, customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"Error": "Customer not found."}), 404
    return customer_schema.jsonify(customer), 200


# Route to update a customer by id
@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@customer_token_required
def update_customer(current_user, customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"Error": "Customer not found."}), 404

    if request.json is None:
        return jsonify({"error": "No JSON data provided"}), 400
    try:
        updated_customer = customer_update_schema.load(
            request.json, instance=customer, partial=True
        )
    except ValidationError as e:
        return {"Error": e.messages}, 400

    if "password" in request.json and request.json["password"]:
        updated_customer.password = request.json["password"]

    db.session.commit()
    return customer_schema.jsonify(updated_customer), 200


# Route to delete a customer by id
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@customer_token_required
def delete_customer(current_user, customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"Error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully."}), 200


# search feature query param
@customers_bp.route("/search", methods=["GET"])
@customer_token_required
def search_customer(current_user):
    name = request.args.get("name")
    if not name:
        return jsonify({"Error": "A 'name' query parameter is required."}), 400

    query = select(Customer).where(Customer.name.like(f"%{name}%"))
    customers = db.session.execute(query).scalars().all()

    if not customers:
        return jsonify({"Message": f"No customers found matching '{name}'."}), 404

    return customers_schema.jsonify(customers), 200
