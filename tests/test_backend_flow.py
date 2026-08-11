import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401  # Ensure all ORM models are registered.


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db
client = TestClient(fastapi_app)


class BackendFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        client.close()
        fastapi_app.dependency_overrides.clear()
        engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def _create_user_and_login(self, email: str) -> str:
        register_response = client.post(
            "/auth/register",
            json={"email": email, "password": "Password123!"},
        )
        self.assertEqual(register_response.status_code, 201, register_response.text)
        self.assertIn("access_token", register_response.json())

        login_response = client.post(
            "/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        self.assertEqual(login_response.status_code, 200, login_response.text)
        payload = login_response.json()
        self.assertIn("access_token", payload)
        return payload["access_token"]

    def test_auth_smoke(self):
        register_response = client.post(
            "/auth/register",
            json={"email": "smoke@example.com", "password": "Password123!"},
        )
        self.assertEqual(register_response.status_code, 201, register_response.text)

        login_response = client.post(
            "/auth/login",
            json={"email": "smoke@example.com", "password": "Password123!"},
        )
        self.assertEqual(login_response.status_code, 200, login_response.text)
        self.assertEqual(login_response.json()["token_type"], "bearer")

    def test_requester_volunteer_and_donation_proof_flow(self):
        requester_token = self._create_user_and_login("requester@example.com")
        donor_token = self._create_user_and_login("donor@example.com")

        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        donor_headers = {"Authorization": f"Bearer {donor_token}"}

        requester_profile_response = client.post(
            "/requester/profile",
            headers=requester_headers,
            json={
                "full_name": "Test Requester",
                "phone": "1234567890",
                "city": "Delhi",
                "state": "Delhi",
            },
        )
        self.assertEqual(requester_profile_response.status_code, 201, requester_profile_response.text)

        blood_request_response = client.post(
            "/blood-request",
            headers=requester_headers,
            json={
                "blood_group": "O+",
                "units_required": 2,
                "hospital_name": "City Hospital",
                "hospital_address": "123 Main St",
                "city": "Delhi",
                "urgency": "high",
                "required_by": "2026-07-23T10:00:00Z",
                "patient_name": "John Doe",
                "relationship_to_patient": "family",
                "remarks": "Urgent",
            },
        )
        self.assertEqual(blood_request_response.status_code, 201, blood_request_response.text)
        request_id = blood_request_response.json()["id"]

        donor_profile_response = client.post(
            "/donor/profile",
            headers=donor_headers,
            json={
                "full_name": "Test Donor",
                "phone": "9876543210",
                "blood_group": "O+",
                "gender": "male",
                "date_of_birth": "1995-01-01",
                "weight": 70,
                "city": "Delhi",
                "state": "Delhi",
                "latitude": 28.61,
                "longitude": 77.2,
            },
        )
        self.assertEqual(donor_profile_response.status_code, 201, donor_profile_response.text)

        volunteer_response = client.post(
            f"/volunteer/{request_id}",
            headers=donor_headers,
        )
        self.assertEqual(volunteer_response.status_code, 201, volunteer_response.text)
        volunteer_id = volunteer_response.json()["id"]

        accept_response = client.patch(
            f"/volunteer/{volunteer_id}/accept",
            headers=requester_headers,
        )
        self.assertEqual(accept_response.status_code, 200, accept_response.text)
        self.assertEqual(accept_response.json()["status"], "accepted")

        proof_response = client.post(
            f"/donation-proof/{request_id}",
            headers=donor_headers,
            json={"proof_file": "https://example.com/proof.jpg"},
        )
        self.assertEqual(proof_response.status_code, 201, proof_response.text)
        self.assertEqual(proof_response.json()["proof_file"], "https://example.com/proof.jpg")

        updated_requests_response = client.get(
            "/blood-request/me",
            headers=requester_headers,
        )
        self.assertEqual(updated_requests_response.status_code, 200, updated_requests_response.text)
        self.assertEqual(updated_requests_response.json()[0]["status"], "DONATION_IN_PROGRESS")

    def test_only_the_requester_can_verify_donation(self):
        requester_token = self._create_user_and_login("owner@example.com")
        other_requester_token = self._create_user_and_login("otherowner@example.com")
        donor_token = self._create_user_and_login("donor2@example.com")

        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        other_requester_headers = {"Authorization": f"Bearer {other_requester_token}"}
        donor_headers = {"Authorization": f"Bearer {donor_token}"}

        client.post(
            "/requester/profile",
            headers=requester_headers,
            json={
                "full_name": "Owner Requester",
                "phone": "1111111111",
                "city": "Delhi",
                "state": "Delhi",
            },
        )
        client.post(
            "/requester/profile",
            headers=other_requester_headers,
            json={
                "full_name": "Other Requester",
                "phone": "2222222222",
                "city": "Delhi",
                "state": "Delhi",
            },
        )
        donor_profile_response = client.post(
            "/donor/profile",
            headers=donor_headers,
            json={
                "full_name": "Donor Two",
                "phone": "3333333333",
                "blood_group": "O+",
                "gender": "female",
                "date_of_birth": "1996-02-02",
                "weight": 65,
                "city": "Delhi",
                "state": "Delhi",
                "latitude": 28.62,
                "longitude": 77.21,
            },
        )
        self.assertEqual(donor_profile_response.status_code, 201, donor_profile_response.text)

        blood_request_response = client.post(
            "/blood-request",
            headers=requester_headers,
            json={
                "blood_group": "O+",
                "units_required": 1,
                "hospital_name": "General Hospital",
                "hospital_address": "456 Side St",
                "city": "Delhi",
                "urgency": "medium",
                "required_by": "2026-07-24T10:00:00Z",
                "patient_name": "Jane Doe",
                "relationship_to_patient": "friend",
                "remarks": "Need help",
            },
        )
        self.assertEqual(blood_request_response.status_code, 201, blood_request_response.text)
        request_id = blood_request_response.json()["id"]

        volunteer_response = client.post(f"/volunteer/{request_id}", headers=donor_headers)
        self.assertEqual(volunteer_response.status_code, 201, volunteer_response.text)
        volunteer_id = volunteer_response.json()["id"]

        accept_response = client.patch(f"/volunteer/{volunteer_id}/accept", headers=requester_headers)
        self.assertEqual(accept_response.status_code, 200, accept_response.text)

        proof_response = client.post(
            f"/donation-proof/{request_id}",
            headers=donor_headers,
            json={"proof_file": "https://example.com/proof-2.jpg"},
        )
        self.assertEqual(proof_response.status_code, 201, proof_response.text)

        unauthorized_verify = client.patch(
            f"/donation-proof/verify/{request_id}",
            headers=other_requester_headers,
        )
        self.assertEqual(unauthorized_verify.status_code, 403, unauthorized_verify.text)

        verify_response = client.patch(
            f"/donation-proof/verify/{request_id}",
            headers=requester_headers,
        )
        self.assertEqual(verify_response.status_code, 200, verify_response.text)
        self.assertEqual(verify_response.json()["status"], "DONATION_VERIFIED")


if __name__ == "__main__":
    unittest.main()
