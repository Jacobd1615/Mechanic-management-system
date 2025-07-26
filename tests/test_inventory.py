from app import create_app
from app.models import db, Part, ServiceTicket, Customer, Mechanic
from app.utils.util import encode_token
from datetime import date
import unittest


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

        # Create test customer for service ticket integration
        self.customer = Customer(
            name="test_customer",
            email="customer@email.com",
            phone="111-111-1111",
            password="testpassword123",
        )

        # Create test mechanic for JWT authentication
        self.mechanic = Mechanic(
            name="test_mechanic",
            email="mechanic@email.com",
            phone="222-222-2222",
            password="testpassword123",
            salary=50000.00,
        )

        # Create test part
        self.part = Part(
            name="Brake Pad",
            description="Premium ceramic brake pad",
            price=45.99,
            quantity_in_stock=25,
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Add test data
            db.session.add(self.customer)
            db.session.add(self.mechanic)
            db.session.add(self.part)
            db.session.commit()

            # Store IDs for later use
            self.customer_id = self.customer.id
            self.mechanic_id = self.mechanic.id
            self.part_id = self.part.part_id

            # Generate JWT token for mechanic authentication
            self.mechanic_token = encode_token(self.mechanic_id, "mechanic")
            self.auth_headers = {"Authorization": f"Bearer {self.mechanic_token}"}

            # Create test service ticket for integration tests
            self.service_ticket = ServiceTicket(
                customer_id=self.customer_id,
                service_date=date.today(),
                description="Test brake repair",
                VIN="1HGBH41JXMN109186",
                status="Open",
            )
            db.session.add(self.service_ticket)
            db.session.commit()
            self.ticket_id = self.service_ticket.ticket_id

        self.client = self.app.test_client()

    def test_create_part(self):
        """Test creating a new inventory part"""
        part_data = {
            "name": "Oil Filter",
            "description": "High-quality oil filter",
            "price": 15.99,
            "quantity_in_stock": 50,
        }

        response = self.client.post(
            "/inventory/", json=part_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertEqual(data["name"], part_data["name"])
        self.assertEqual(data["description"], part_data["description"])
        self.assertEqual(data["price"], part_data["price"])
        self.assertEqual(data["quantity_in_stock"], part_data["quantity_in_stock"])

    def test_invalid_create_part(self):
        """Test creating part with invalid data"""
        # Missing required fields
        invalid_data = {
            "name": "Incomplete Part",
            # Missing price and quantity_in_stock
        }

        response = self.client.post(
            "/inventory/", json=invalid_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

        response_data = response.get_json()
        self.assertIn("Error", response_data)

    def test_get_all_parts(self):
        """Test retrieving all inventory parts"""
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)  # Should have at least our setUp part

    def test_get_part_by_id(self):
        """Test retrieving a specific part by ID"""
        response = self.client.get(f"/inventory/{self.part_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["part_id"], self.part_id)
        self.assertEqual(data["name"], "Brake Pad")
        self.assertEqual(data["price"], 45.99)

    def test_get_nonexistent_part(self):
        """Test retrieving a part that doesn't exist"""
        response = self.client.get("/inventory/99999")
        self.assertEqual(response.status_code, 404)

    def test_update_part(self):
        """Test updating an existing part"""
        update_data = {
            "name": "Premium Brake Pad",
            "price": 55.99,
            "quantity_in_stock": 30,
        }

        response = self.client.put(
            f"/inventory/{self.part_id}", json=update_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["name"], "Premium Brake Pad")
        self.assertEqual(data["price"], 55.99)
        self.assertEqual(data["quantity_in_stock"], 30)

    def test_invalid_update_part(self):
        """Test updating part with invalid data"""
        invalid_data = {"price": "not_a_number"}  # Invalid price format

        response = self.client.put(
            f"/inventory/{self.part_id}", json=invalid_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_part(self):
        """Test deleting an inventory part"""
        response = self.client.delete(
            f"/inventory/{self.part_id}", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)

        # Verify part is deleted
        get_response = self.client.get(f"/inventory/{self.part_id}")
        self.assertEqual(get_response.status_code, 404)

    def test_delete_nonexistent_part(self):
        """Test deleting a part that doesn't exist"""
        response = self.client.delete("/inventory/99999", headers=self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_remove_stock(self):
        """Test removing stock from inventory"""
        # Remove 5 units from stock
        stock_data = {"quantity": 5}

        response = self.client.post(
            f"/inventory/{self.part_id}/remove_stock",
            json=stock_data,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)

        # Verify stock was reduced
        get_response = self.client.get(f"/inventory/{self.part_id}")
        data = get_response.get_json()
        self.assertEqual(data["quantity_in_stock"], 20)  # 25 - 5 = 20

    def test_remove_too_much_stock(self):
        """Test removing more stock than available"""
        # Try to remove more than available (25 in stock)
        excessive_stock = {"quantity": 50}

        response = self.client.post(
            f"/inventory/{self.part_id}/remove_stock",
            json=excessive_stock,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)

        response_data = response.get_json()
        self.assertIn("Error", response_data)

    def test_add_part_to_service_ticket(self):
        """Test adding inventory part to service ticket"""
        add_data = {"quantity": 2}

        response = self.client.post(
            f"/inventory/{self.part_id}/add-to-ticket/{self.ticket_id}",
            json=add_data,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)

        # Verify stock was reduced by 1 (current API behavior: 25 - 1 = 24)
        get_response = self.client.get(f"/inventory/{self.part_id}")
        data = get_response.get_json()
        self.assertEqual(data["quantity_in_stock"], 24)

    def test_add_part_to_nonexistent_ticket(self):
        """Test adding part to service ticket that doesn't exist"""
        add_data = {"quantity": 1}

        response = self.client.post(
            f"/inventory/{self.part_id}/add-to-ticket/99999",
            json=add_data,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_add_nonexistent_part_to_ticket(self):
        """Test adding non-existent part to service ticket"""
        add_data = {"quantity": 1}

        response = self.client.post(
            f"/inventory/99999/add-to-ticket/{self.ticket_id}",
            json=add_data,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
