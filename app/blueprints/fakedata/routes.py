# Fake data generation routes will be defined here
from flask import jsonify
from . import fakedata_bp
from app.models import (
    db,
    Customer,
    Mechanic,
    ServiceTicket,
    LaborLog,
    Part,
    mechanic_association,
    service_ticket_part_association,
)
from faker import Faker
import random


@fakedata_bp.route("/seed-database", methods=["POST"])
def seed_database():
    """Clear existing data and seed the database with fake data."""

    # Step 1: Clear existing data (respect FK constraints)
    db.session.execute(mechanic_association.delete())
    db.session.execute(service_ticket_part_association.delete())
    db.session.query(LaborLog).delete()
    db.session.query(ServiceTicket).delete()
    db.session.query(Part).delete()
    db.session.query(Customer).delete()
    db.session.query(Mechanic).delete()
    db.session.commit()

    faker = Faker()
    customers = []
    mechanics = []
    tickets = []
    parts = []

    # Step 3: Create Customers
    for _ in range(100):
        customer = Customer(
            name=faker.name(),
            email=faker.unique.email(),
            phone=faker.phone_number(),
            password=faker.password(),
        )
        customers.append(customer)
        db.session.add(customer)

    # Step 4: Create Mechanics
    for _ in range(20):
        mechanic = Mechanic(
            name=faker.name(),
            email=faker.unique.email(),
            phone=faker.phone_number(),
            salary=faker.random_int(min=45000, max=120000),
            password=faker.password(),
        )
        mechanics.append(mechanic)
        db.session.add(mechanic)

    # Step 5: Create Parts
    for _ in range(50):
        part = Part(
            name=faker.word(),
            description=faker.sentence(),
            price=round(random.uniform(10, 500), 2),
            quantity_in_stock=random.randint(1, 100),
        )
        parts.append(part)
        db.session.add(part)

    db.session.commit()

    # Step 6: Create Service Tickets with mechanics + parts
    for _ in range(100):
        customer = random.choice(customers)
        ticket = ServiceTicket(
            customer_id=customer.id,
            service_date=faker.date_between(start_date="-2y", end_date="today"),
            description=faker.sentence(),
            VIN=faker.unique.vin(),
        )
        # Attach 1–3 mechanics
        ticket.mechanics.extend(random.sample(mechanics, random.randint(1, 3)))

        # Attach 0–5 parts
        ticket.parts.extend(random.sample(parts, random.randint(0, 5)))

        tickets.append(ticket)
        db.session.add(ticket)

    db.session.commit()

    # Step 7: Create Labor Logs for each ticket/mechanic pair
    for ticket in tickets:
        for mechanic in ticket.mechanics:
            labor_log = LaborLog(
                ticket_id=ticket.ticket_id,
                mechanic_id=mechanic.id,
                hours_worked=round(random.uniform(1, 8), 2),
            )
            db.session.add(labor_log)

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Database seeded successfully.",
                "customers": len(customers),
                "mechanics": len(mechanics),
                "parts": len(parts),
                "service_tickets": len(tickets),
                "labor_logs": db.session.query(LaborLog).count(),
            }
        ),
        200,
    )
