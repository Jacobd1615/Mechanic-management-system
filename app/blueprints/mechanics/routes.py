# Mechanic routes will be defined here
# routes for the mechanics
from .schemas import (
    mechanic_schema,
    mechanics_schema,
    login_schema,
    mechanic_update_schema,
)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, func
from app.models import Mechanic, db, ServiceTicket, LaborLog, mechanic_association
from . import mechanics_bp
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_mechanic_token
from app.utils.roles import mechanic_token_required


# routes for mechanic
@mechanics_bp.route("/login", methods=["POST"])
@limiter.limit("5/minute")  # Add rate limit to prevent brute-force attacks
def login():
    try:
        if request.json is None:
            return jsonify({"messages": "No JSON data provided"}), 400
        # Validate the request data using the login_schema
        credentials = login_schema.load(request.json)
        email = credentials.email
        password = credentials.password
    except ValidationError as e:
        return jsonify({"messages": e.messages}), 400

    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalar_one_or_none()

    if mechanic and mechanic.password == password:
        auth_token = encode_mechanic_token(mechanic.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token,
        }
        print(" welcome back, " + mechanic.name + "!")
        return jsonify(response), 200
    else:
        return jsonify({"messages": "Invalid email or password"}), 401


# creating new mechanic
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    # Get json data from request
    try:
        if request.json is None:
            return jsonify({"error": "No JSON data provided"}), 400
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return {"Error": e.messages}, 400

    # Check to see if mechanic already exists
    query = select(Mechanic).where(Mechanic.email == mechanic_data.email)
    existing_mechanic = db.session.execute(query).scalar_one_or_none()
    if existing_mechanic:
        return {"Error": "Mechanic with this email already exists."}, 400

    # Create new mechanic - mechanic_data is already a Mechanic object
    db.session.add(mechanic_data)
    db.session.commit()
    print("New mechanic created successfully.")
    return mechanic_schema.jsonify(mechanic_data), 201


# get all mechanics
@mechanics_bp.route("/", methods=["GET"])
@mechanic_token_required
def get_mechanics(current_user):
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics)
    except (TypeError, ValueError):
        # Query all mechanics from the database
        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(mechanics), 200


# get a mechanic by id
@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
@mechanic_token_required
def get_mechanic(current_user, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"Error": "Mechanic not found."}), 404
    return mechanic_schema.jsonify(mechanic), 200


# update a mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
@mechanic_token_required
def update_mechanic(current_user, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"Error": "Mechanic not found."}), 404

    if request.json is None:
        return jsonify({"error": "No JSON data provided"}), 400
    try:
        updated_mechanic = mechanic_update_schema.load(
            request.json, instance=mechanic, partial=True
        )
    except ValidationError as e:
        return {"Error": e.messages}, 400

    if "password" in request.json and request.json["password"]:
        updated_mechanic.password = request.json["password"]

    db.session.commit()
    return mechanic_schema.jsonify(updated_mechanic), 200


# delete a mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@mechanic_token_required
def delete_mechanic(current_user, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"Error": "Mechanic not found."}), 404

    # Check if mechanic has any labor logs
    if mechanic.labor_logs:
        return (
            jsonify(
                {
                    "Error": "Cannot delete mechanic with existing labor logs. "
                    "Please reassign or remove labor logs first."
                }
            ),
            400,
        )

    # Check if mechanic has any service tickets assigned
    if mechanic.service_tickets:
        return (
            jsonify(
                {
                    "Error": "Cannot delete mechanic with assigned service tickets. "
                    "Please reassign tickets first."
                }
            ),
            400,
        )

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic deleted successfully."}), 200


# get all service tickets for a mechanic
@mechanics_bp.route("/<int:mechanic_id>/service_tickets", methods=["GET"])
@mechanic_token_required
def get_service_tickets(current_user, mechanic_id):
    if current_user.id != mechanic_id:
        return (
            jsonify(
                {
                    "Error": f"Access denied. You (mechanic ID {current_user.id}) are not authorized to view service tickets for mechanic ID {mechanic_id}. You can only view your own tickets."
                }
            ),
            403,
        )

    # Get the mechanic object first
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"Error": "Mechanic not found."}), 404

    # Query service tickets that contain this mechanic
    query = select(ServiceTicket).where(ServiceTicket.mechanics.contains(mechanic))
    service_tickets = db.session.execute(query).scalars().all()
    return (
        jsonify(
            [
                {
                    "ticket_id": ticket.ticket_id,
                    "description": ticket.description,
                    "status": ticket.status,
                    "date_created": ticket.date_created,
                    "date_completed": ticket.date_completed,
                    "customer_name": ticket.customer.name,
                    "VIN": ticket.VIN,
                    "service_date": ticket.service_date,
                    "labor_logs": [
                        {
                            "log_id": log.id,
                            "mechanic_id": log.mechanic_id,
                            "hours_worked": log.hours_worked,
                            "date_logged": log.date_logged,
                        }
                        for log in ticket.labor_logs
                    ],
                }
                for ticket in service_tickets
            ]
        ),
        200,
    )


# New route for the report
@mechanics_bp.route("/reports/top_labor_by_ticket", methods=["GET"])
@cache.cached(timeout=60)  # Cache the report for 60 seconds
def get_top_labor_report():
    """
    Generates a report of the mechanic who worked the most hours on each ticket
    using Python sorting.
    """
    # 1. Fetch ALL tickets from the database
    all_tickets = db.session.execute(select(ServiceTicket)).scalars().all()

    report = []

    # 2. Loop through every single ticket
    for ticket in all_tickets:
        if not ticket.labor_logs:
            continue  # Skip tickets with no labor logged

        # 3. For each ticket, create a dictionary to hold hours per mechanic
        mechanic_hours = {}
        for log in ticket.labor_logs:
            mechanic_name = log.mechanic.name
            if mechanic_name not in mechanic_hours:
                mechanic_hours[mechanic_name] = 0
            mechanic_hours[mechanic_name] += log.hours_worked

        # 4. Find the top mechanic for the current ticket
        if not mechanic_hours:
            continue

        # Sort the mechanics by hours worked (descending)
        top_mechanic_name, top_hours = sorted(
            mechanic_hours.items(), key=lambda item: item[1], reverse=True
        )[0]

        # 5. Append the result to our final report
        report.append(
            {
                "ticket_id": ticket.ticket_id,
                "ticket_description": ticket.description,
                "top_mechanic": top_mechanic_name,
                "total_hours_logged": top_hours,
            }
        )

    return jsonify(report), 200


# New route for mechanics ranked by ticket count
@mechanics_bp.route("/reports/most_tickets_worked", methods=["GET"])
@cache.cached(timeout=60)  # Cache the report for 60 seconds
def get_mechanics_by_ticket_count():
    """
    Returns a list of mechanics ordered by the number of tickets they have worked on,
    calculated using Python's sorted() function.
    """
    # 1. Fetch all mechanics from the database
    all_mechanics = db.session.execute(select(Mechanic)).scalars().all()

    # 2. Create a list of mechanic data, including the count of tickets they are assigned to
    mechanic_ticket_counts = []
    for mechanic in all_mechanics:
        mechanic_ticket_counts.append(
            {
                "mechanic_id": mechanic.id,
                "name": mechanic.name,
                "email": mechanic.email,
                "tickets_worked_on": len(mechanic.service_tickets),
            }
        )

    # 3. Sort the list of mechanics by the 'tickets_worked_on' count in descending order
    sorted_report = sorted(
        mechanic_ticket_counts, key=lambda m: m["tickets_worked_on"], reverse=True
    )

    return jsonify(sorted_report), 200
