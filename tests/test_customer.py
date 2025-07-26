from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token
import unittest


class TestMember(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(
            name="test_user",
            email="test@email.com",
            phone="111-111-1111",
            password="testpassword123",
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    # customer login test
    def test_login_customer(self):
        credentials = {"email": "test@email.com", "password": "testpassword123"}

        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        return response.json["auth_token"]

    def test_invaild_login(self):
        credentials = {"email": "bad_email@email.com", "password": "bad_pw"}

        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 400)
        # Check the actual error message structure
        response_data = response.get_json()
        self.assertIn("messages", response_data)

    # Create Customer test
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@example.com",
            "phone": "540-540-9999",
            "password": "12345678",
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "John Doe")

    def test_invalid_creating(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "543-543-999",
            "password": "12345678",
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertEqual(
            response_data["Error"]["email"], ["Missing data for required field."]
        )

    # Update Customer test
    def test_update_customer(self):
        # Only update the name field, don't send empty strings for validated fields
        update_payload = {"name": "Peter"}

        headers = {"Authorization": "Bearer " + self.test_login_customer()}

        # Use customer ID 1 (the test customer we created in setUp)
        response = self.client.put("/customers/1", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Peter")
        self.assertEqual(response.json["email"], "test@email.com")

    def test_invaild_update_customer(self):
        update_payload = {
            "email": "invalid_email_format"
        }  # This will trigger validation error

        headers = {
            "Authorization": "Bearer " + self.test_login_customer()
        }  # Added space after Bearer

        # Use customer ID 1 (the test customer we created in setUp)
        response = self.client.put("/customers/1", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        # Check that an error message exists
        response_data = response.get_json()
        self.assertIn("Error", response_data)

    # Get all customers test
    def test_get_all_customers(self):
        headers = {"Authorization": "Bearer " + self.test_login_customer()}

        response = self.client.get("/customers/", headers=headers)
        self.assertEqual(response.status_code, 200)
        # Should return a list containing our test customer
        customers = response.get_json()
        self.assertIsInstance(customers, list)
        self.assertTrue(len(customers) >= 1)

    # Invalid get all customers test (no auth)
    def test_invalid_get_all_customers(self):
        # Try to get customers without authorization header
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 401)
        response_data = response.get_json()
        self.assertIn("message", response_data)

    # Delete customer test
    def test_delete_customer(self):
        headers = {"Authorization": "Bearer " + self.test_login_customer()}

        # Delete customer ID 1 (the test customer we created in setUp)
        response = self.client.delete("/customers/1", headers=headers)
        self.assertEqual(response.status_code, 200)

        # After deleting the customer, their token becomes invalid
        # So we expect 401 (Unauthorized) when trying to access with that token
        get_response = self.client.get("/customers/1", headers=headers)
        self.assertEqual(get_response.status_code, 401)

    # Invalid delete customer test
    def test_invalid_delete_customer(self):
        headers = {"Authorization": "Bearer " + self.test_login_customer()}

        # Try to delete a customer that doesn't exist
        response = self.client.delete("/customers/999", headers=headers)
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()