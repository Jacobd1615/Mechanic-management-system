from app import create_app
from app.models import db, Mechanic
from app.utils.util import encode_token
import unittest


class testMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.mechanic = Mechanic(
            name="test_user",
            email="test@email.com",
            phone="111-111-1111",
            password="testpassword123",
            salary="50000.00",
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    # mechanic login test
    def test_login_mechanic(self):
        credentials = {"email": "test@email.com", "password": "testpassword123"}

        response = self.client.post("/mechanics/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "success")
        # Test that auth_token exists
        response_data = response.get_json()
        self.assertIn("auth_token", response_data)

    def get_mechanic_token(self):
        """Helper method to get auth token for authenticated requests"""
        credentials = {"email": "test@email.com", "password": "testpassword123"}
        response = self.client.post("/mechanics/login", json=credentials)
        return response.get_json()["auth_token"]

    def test_invaild_mechanic(self):
        credentials = {"email": "bad_email@email.com", "password": "bad_pw"}

        response = self.client.post("/mechanics/login", json=credentials)
        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertIn("messages", response_data)

    # Create Mechanic test
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "jd@example.com",
            "phone": "540-540-9999",
            "password": "12345678",
            "salary": "50000.00",
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "John Doe")

    def test_invalid_creating(self):
        mechanic_payload = {
            "name": "John Doe",
            "phone": "543-543-999",
            "password": "12345678",
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertEqual(
            response_data["Error"]["email"], ["Missing data for required field."]
        )

    # Update Mechanic test
    def test_update_mechanic(self):
        # Only update the name field, don't send empty strings for validated fields
        update_payload = {"name": "Peter"}

        headers = {"Authorization": "Bearer " + self.get_mechanic_token()}

        # Use mechanic ID 1 (the test mechanic we created in setUp)
        response = self.client.put("/mechanics/1", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Peter")
        self.assertEqual(response.get_json()["email"], "test@email.com")

    def test_invalid_update_mechanic(self):
        update_payload = {
            "email": "invalid_email_format"
        }  # This will trigger validation error

        headers = {
            "Authorization": "Bearer " + self.get_mechanic_token()
        }  # Added space after Bearer

        # Use mechanic ID 1 (the test mechanic we created in setUp)
        response = self.client.put("/mechanics/1", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        # Check that an error message exists
        response_data = response.get_json()
        self.assertIn("Error", response_data)

    # Get all mechanics test
    def test_get_all_mechanics(self):
        headers = {"Authorization": "Bearer " + self.get_mechanic_token()}

        response = self.client.get("/mechanics/", headers=headers)
        self.assertEqual(response.status_code, 200)
        # Should return a list containing our test mechanic
        mechanics = response.get_json()
        self.assertIsInstance(mechanics, list)
        self.assertTrue(len(mechanics) >= 1)

    # Invalid get all mechanics test (no auth)
    def test_invalid_get_all_mechanics(self):
        # Try to get mechanics without authorization header
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 401)
        response_data = response.get_json()
        self.assertIn("message", response_data)

    # Delete mechanic test
    def test_delete_mechanic(self):
        headers = {"Authorization": "Bearer " + self.get_mechanic_token()}

        # Delete mechanic ID 1 (the test mechanic we created in setUp)
        response = self.client.delete("/mechanics/1", headers=headers)
        self.assertEqual(response.status_code, 200)

        # After deleting the mechanic, their token becomes invalid
        # So we expect 401 (Unauthorized) when trying to access with that token
        get_response = self.client.get("/mechanics/1", headers=headers)
        self.assertEqual(get_response.status_code, 401)

    # Invalid delete mechanic test
    def test_invalid_delete_mechanic(self):
        headers = {"Authorization": "Bearer " + self.get_mechanic_token()}

        # Try to delete a mechanic that doesn't exist
        response = self.client.delete("/mechanics/999", headers=headers)
        self.assertEqual(response.status_code, 404)
