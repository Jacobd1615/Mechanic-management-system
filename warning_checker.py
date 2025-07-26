#!/usr/bin/env python3
import warnings
import sys


# Capture all warnings and print them
def custom_warn_handler(message, category, filename, lineno, file=None, line=None):
    print(f"\n=== WARNING ===")
    print(f"Category: {category.__name__}")
    print(f"Message: {message}")
    print(f"File: {filename}")
    print(f"Line: {lineno}")
    if line:
        print(f"Code: {line.strip()}")
    print("=" * 50)


warnings.showwarning = custom_warn_handler
warnings.filterwarnings("always")

print("Checking for API warnings...")

try:
    # Import all major components to trigger any warnings
    from app import create_app
    from app.models import db, Mechanic, Customer, ServiceTicket, Part, LaborLog
    from app.blueprints.mechanics import routes as mechanic_routes
    from app.blueprints.customers import routes as customer_routes
    from app.blueprints.inventory import routes as inventory_routes
    from app.blueprints.service_tickets import routes as ticket_routes

    print("All imports successful - checking for schema warnings...")

    # Create app and test schemas
    app = create_app("TestingConfig")
    with app.app_context():
        # Import schemas to trigger any marshmallow warnings
        from app.blueprints.mechanics.schemas import mechanic_schema
        from app.blueprints.customers.schemas import customer_schema
        from app.blueprints.inventory.schemas import part_schema
        from app.blueprints.service_tickets.schemas import service_ticket_schema

        print("Schema imports successful - testing schema operations...")

        # Test schema operations that might trigger warnings
        test_data = {
            "name": "Test Mechanic",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "password": "testpass123",
            "salary": 50000.00,
        }

        # Test load operation
        result = mechanic_schema.load(test_data)
        print(f"Schema load test successful: {type(result)}")

        print("All tests completed successfully!")

except Exception as e:
    print(f"Error during testing: {e}")
    import traceback

    traceback.print_exc()
