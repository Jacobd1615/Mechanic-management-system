# Inventory routes will be defined here
# routes for the inventory
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Part, db, ServiceTicket
from .schemas import part_schema, parts_schema
from . import inventory_bp
from app.extensions import limiter, cache

PART_NOT_FOUND = "Part not found"


# Create a new part
@inventory_bp.route("/", methods=["POST"])
@limiter.limit("10/hour")
def create_part():
    if not request.json:
        return jsonify({"Error": "No JSON data provided"}), 400
    try:
        # Use the schema to load and validate the data
        new_part = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error": e.messages}), 400

    db.session.add(new_part)
    db.session.commit()
    return part_schema.jsonify(new_part), 201


# Get all parts
@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)
def get_all_parts():
    query = select(Part)
    parts = db.session.execute(query).scalars().all()
    return parts_schema.jsonify(parts), 200


# Get a single part by ID
@inventory_bp.route("/<int:part_id>", methods=["GET"])
@cache.cached(timeout=60)
def get_part(part_id):
    part = db.session.get(Part, part_id)
    if not part:
        return jsonify({"Error": PART_NOT_FOUND}), 404
    return part_schema.jsonify(part), 200


# Update a part
@inventory_bp.route("/<int:part_id>", methods=["PUT"])
@limiter.limit("10/minute")
def update_part(part_id):
    part = db.session.get(Part, part_id)
    if not part:
        return jsonify({"Error": PART_NOT_FOUND}), 404
    if not request.json:
        return jsonify({"Error": "No JSON data provided"}), 400
    try:
        # Use partial=True to allow partial updates
        # Pass the existing instance and the session to the schema's load method.
        # This will update the 'part' object in place.
        part = part_schema.load(
            request.json, session=db.session, instance=part, partial=True
        )
    except ValidationError as e:
        return jsonify({"Error": e.messages}), 400

    # The part object is already updated by schema.load, so no loop is needed.
    db.session.commit()
    return part_schema.jsonify(part), 200


# Delete a part
@inventory_bp.route("/<int:part_id>", methods=["DELETE"])
@limiter.limit("5/hour")
def delete_part(part_id):
    part = db.session.get(Part, part_id)
    if not part:
        return jsonify({"Error": PART_NOT_FOUND}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({"Message": f"{part.name} with id {part_id} has been deleted."}), 200


# Route to reduce the stock of a specific part
@inventory_bp.route("/<int:part_id>/remove_stock", methods=["POST"])
@limiter.limit("20/minute")
def remove_part_stock(part_id):
    part = db.session.get(Part, part_id)
    if not part:
        return jsonify({"Error": PART_NOT_FOUND}), 404

    if not request.json or "quantity" not in request.json:
        return jsonify({"Error": "Missing 'quantity' in request body"}), 400

    try:
        quantity_to_remove = int(request.json["quantity"])
        if quantity_to_remove <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"Error": "Invalid quantity. Must be a positive integer."}), 400

    if part.quantity_in_stock < quantity_to_remove:
        return (
            jsonify(
                {
                    "Error": "Cannot remove more parts than are in stock.",
                    "quantity_in_stock": part.quantity_in_stock,
                }
            ),
            400,
        )

    part.quantity_in_stock -= quantity_to_remove
    db.session.commit()

    return (
        jsonify(
            {
                "Message": f"Removed {quantity_to_remove} units from {part.name}.",
                "new_quantity_in_stock": part.quantity_in_stock,
            }
        ),
        200,
    )


# Route to add a part to a service ticket
@inventory_bp.route("/<int:part_id>/add-to-ticket/<int:ticket_id>", methods=["POST"])
def add_part_to_ticket(part_id, ticket_id):
    part = db.session.get(Part, part_id)
    if not part:
        return jsonify({"Error": PART_NOT_FOUND}), 404

    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"Error": "Service ticket not found"}), 404

    if part in ticket.parts:
        return jsonify({"Message": "Part already added to this ticket"}), 200

    if part.quantity_in_stock < 1:
        return jsonify({"Error": "Not enough parts in stock"}), 400

    ticket.parts.append(part)
    part.quantity_in_stock -= 1
    db.session.commit()

    return (
        jsonify({"Message": f"Part {part.name} added to ticket {ticket.ticket_id}"}),
        200,
    )
