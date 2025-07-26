# Service ticket routes will be defined here
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import (
    ServiceTicket,
    db,
    Mechanic,
    Customer,
    LaborLog,
    Part,
)
from .schemas import (
    service_ticket_schema,
    service_tickets_schema,
    edit_service_ticket_schema,
    labor_log_schema,
)
from app.blueprints.inventory.schemas import part_schema
from app.extensions import limiter
from . import service_tickets_bp  # Import the blueprint from __init__.py
from app.extensions import cache
from app.utils.roles import (
    customer_token_required,
    mechanic_token_required,
)


# Route for creating a new service ticket
@service_tickets_bp.route("/", methods=["POST"])
@limiter.limit("10/hour")  # Rate limit: 10 requests per hour per IP
@customer_token_required
def create_service_ticket(current_user):
    if not request.json:
        return jsonify({"Error": "No JSON data provided"}), 400

    try:
        # Validate and deserialize the request data, customer_id is not required
        ticket_data = service_ticket_schema.load(request.json, partial=("customer_id",))
    except ValidationError as e:
        return jsonify({"Error": e.messages}), 400

    # The customer is the user who is logged in.
    customer_query = select(Customer).where(Customer.id == current_user.id)
    customer = db.session.execute(customer_query).scalars().first()
    if not customer:
        return jsonify({"Error": f"Customer with id {current_user.id} not found."}), 404

    # Create and save the new service ticket
    new_ticket = ServiceTicket(
        customer_id=current_user.id,
        service_date=ticket_data["service_date"],
        VIN=ticket_data["VIN"],
        description=ticket_data["description"],
    )
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(new_ticket)), 201


# Route to get all service tickets
@service_tickets_bp.route("/", methods=["GET"])
@cache.cached(timeout=15)  # Cache this route for 15 seconds
def get_all_service_tickets():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        query = select(ServiceTicket)
        tickets = db.paginate(query, page=page, per_page=per_page)
        return jsonify(service_tickets_schema.dump(tickets))
    except (TypeError, ValueError):
        query = select(ServiceTicket)
        tickets = db.session.execute(query).scalars().all()
        return jsonify(service_tickets_schema.dump(tickets)), 200


# New route for a customer to get their own tickets
@service_tickets_bp.route("/my-tickets", methods=["GET"])
@customer_token_required
@cache.cached(timeout=30)
def get_my_tickets(current_user):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == current_user.id)
    my_tickets = db.session.execute(query).scalars().all()
    if not my_tickets:
        return jsonify({"message": "You have no service tickets."}), 200
    return jsonify(service_tickets_schema.dump(my_tickets)), 200


# Route to get a service ticket by ID
@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@cache.cached(timeout=30)
def find_service_ticket(ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.ticket_id == ticket_id)
    ticket = db.session.execute(query).scalars().first()
    if not ticket:
        return jsonify({"Error": "Service ticket not found."}), 404
    return jsonify(service_ticket_schema.dump(ticket)), 200


# Route to delete a service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
@limiter.limit("5/hour")
def delete_service_ticket(ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.ticket_id == ticket_id)
    ticket = db.session.execute(query).scalars().first()
    if not ticket:
        return jsonify({"Error": "Service ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()
    return (
        jsonify({"Message": f"Service ticket with id {ticket_id} has been deleted."}),
        200,
    )


# Route to assign a mechanic to a service ticket
@service_tickets_bp.route(
    "/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def assign_mechanic_to_ticket(ticket_id, mechanic_id):
    ticket_query = select(ServiceTicket).where(ServiceTicket.ticket_id == ticket_id)
    ticket = db.session.execute(ticket_query).scalars().first()
    if not ticket:
        return jsonify({"Error": "Service ticket not found"}), 404

    mechanic_query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(mechanic_query).scalars().first()
    if not mechanic:
        return jsonify({"Error": "Mechanic not found"}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"Message": "Mechanic already assigned to this ticket"}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()

    return (
        jsonify(
            {
                "Message": f"Mechanic {mechanic.name} assigned to ticket {ticket.ticket_id}"
            }
        ),
        200,
    )


# Route to remove a mechanic from a service ticket
@service_tickets_bp.route(
    "/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def remove_mechanic_from_ticket(current_user, ticket_id, mechanic_id):
    ticket_query = select(ServiceTicket).where(ServiceTicket.ticket_id == ticket_id)
    ticket = db.session.execute(ticket_query).scalars().first()
    if not ticket:
        return jsonify({"Error": "Service ticket not found"}), 404

    mechanic_query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(mechanic_query).scalars().first()
    if not mechanic:
        return jsonify({"Error": "Mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"Error": "Mechanic is not assigned to this ticket"}), 404

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return (
        jsonify(
            {
                "Message": f"Mechanic {mechanic.name} removed from ticket {ticket.ticket_id}"
            }
        ),
        200,
    )


# Route for updating a service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
@limiter.limit("10/minute")
@customer_token_required
def update_service_ticket(current_user, ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.ticket_id == ticket_id)
    ticket = db.session.execute(query).scalars().first()
    if not ticket:
        return jsonify({"Error": "Service ticket not found"}), 404
    if ticket.customer_id != current_user.id:
        return jsonify({"Error": "You are not authorized to update this ticket."}), 403

    if not request.json:
        return jsonify({"Error": "No JSON data provided"}), 400

    try:
        # Load and validate the new data
        ticket_data = service_ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify({"Error": e.messages}), 400

    # Update the ticket instance with the new data
    for field, value in ticket_data.items():
        setattr(ticket, field, value)

    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


# Route to add/remove mechanics from a service ticket
@service_tickets_bp.route("/<int:ticket_id>/edit-mechanics", methods=["PUT"])
@customer_token_required
def edit_ticket_mechanics(current_user, ticket_id):
    ticket_query = select(ServiceTicket).where(ServiceTicket.ticket_id == ticket_id)
    ticket = db.session.execute(ticket_query).scalars().first()
    if not ticket:
        return jsonify({"Error": "Service ticket not found"}), 404

    if not request.json:
        return jsonify({"Error": "No JSON data provided"}), 400

    try:
        data = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": e.messages}), 400

    # Add mechanics
    if "add_mechanic_ids" in data:
        for mechanic_id in data["add_mechanic_ids"]:
            mechanic_query = select(Mechanic).where(Mechanic.id == mechanic_id)
            mechanic = db.session.execute(mechanic_query).scalars().first()
            if mechanic and mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)

    # Remove mechanics
    if "remove_mechanic_ids" in data:
        for mechanic_id in data["remove_mechanic_ids"]:
            mechanic_query = select(Mechanic).where(Mechanic.id == mechanic_id)
            mechanic = db.session.execute(mechanic_query).scalars().first()
            if mechanic and mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)

    db.session.add(ticket)  # Explicitly add the ticket to the session
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


# Route to log labor hours for a mechanic on a specific ticket
@service_tickets_bp.route("/<int:ticket_id>/labor", methods=["POST"])
@mechanic_token_required
def add_labor_to_ticket(current_user, ticket_id):
    # 1. Find the service ticket
    ticket_query = select(ServiceTicket).where(ServiceTicket.ticket_id == ticket_id)
    ticket = db.session.execute(ticket_query).scalars().first()
    if not ticket:
        return jsonify({"Error": "Service ticket not found"}), 404

    # 2. Validate the request body
    if (
        not request.json
        or "mechanic_id" not in request.json
        or "hours_worked" not in request.json
    ):
        return (
            jsonify({"Error": "Request must include mechanic_id and hours_worked"}),
            400,
        )

    mechanic_id = request.json["mechanic_id"]
    hours_worked = request.json["hours_worked"]

    # 3. Find the mechanic
    mechanic_query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(mechanic_query).scalars().first()
    if not mechanic:
        return jsonify({"Error": "Mechanic not found"}), 404

    # 4. IMPORTANT: Check if the mechanic is actually assigned to this ticket
    if mechanic not in ticket.mechanics:
        return (
            jsonify(
                {"Error": f"Mechanic {mechanic.name} is not assigned to this ticket."}
            ),
            400,
        )

    # 5. IMPORTANT: Check if the mechanic is logging their own hours
    if current_user.id != mechanic_id:
        return jsonify({"Error": "You can only log hours for yourself."}), 403

    # 6. Create the new LaborLog entry
    new_labor_log = LaborLog(
        ticket_id=ticket.ticket_id, mechanic_id=mechanic.id, hours_worked=hours_worked
    )

    db.session.add(new_labor_log)
    db.session.commit()

    return jsonify(labor_log_schema.dump(new_labor_log)), 201


# Route to update a labor log entry
@service_tickets_bp.route("/labor/<int:labor_log_id>", methods=["PUT"])
@mechanic_token_required
def update_labor_log(current_user, labor_log_id):
    labor_log_query = select(LaborLog).where(LaborLog.id == labor_log_id)
    labor_log = db.session.execute(labor_log_query).scalars().first()
    if not labor_log:
        return jsonify({"Error": "Labor log not found"}), 404

    if labor_log.mechanic_id != current_user.id:
        return (
            jsonify({"Error": "You are not authorized to update this labor log."}),
            403,
        )

    if not request.json or "hours_worked" not in request.json:
        return jsonify({"Error": "Request must include hours_worked"}), 400

    try:
        hours = float(request.json["hours_worked"])
        if hours < 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"Error": "hours worked must be a positive number"}), 400

    labor_log.hours_worked = hours
    db.session.commit()

    return jsonify(labor_log_schema.dump(labor_log)), 200


# Route to delete a labor log entry
@service_tickets_bp.route("/labor/<int:labor_log_id>", methods=["DELETE"])
def delete_labor_log(labor_log_id):
    labor_log_query = select(LaborLog).where(LaborLog.id == labor_log_id)
    labor_log = db.session.execute(labor_log_query).scalars().first()
    if not labor_log:
        return jsonify({"Error": "Labor log not found"}), 404

    db.session.delete(labor_log)
    db.session.commit()

    return (
        jsonify({"Message": f"Labor log with id {labor_log_id} has been deleted."}),
        200,
    )
