import os
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401  # Ensure all ORM models are registered.

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:Gulam123@localhost:5432/hemo_test",
)

engine = create_engine(TEST_DATABASE_URL)
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

    def _create_requester_profile(
        self, headers: dict, full_name: str = "Test Requester"
    ):
        response = client.post(
            "/requester/profile",
            headers=headers,
            json={
                "full_name": full_name,
                "phone": "9876543210",
                "city": "Delhi",
                "state": "Delhi",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def _create_blood_request(self, headers: dict, blood_group: str = "O+"):
        response = client.post(
            "/blood-request",
            headers=headers,
            json={
                "blood_group": blood_group,
                "units_required": 2,
                "hospital_name": "Test Hospital",
                "hospital_address": "Connaught Place",
                "city": "Delhi",
                "urgency": "high",
                "required_by": "2026-08-20T18:00:00",
                "patient_name": "Test Patient",
                "relationship_to_patient": "family",
                "remarks": "Urgent requirement",
                "latitude": 28.6139,
                "longitude": 77.2090,
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def _create_donor_profile(
        self,
        headers: dict,
        full_name: str,
        blood_group: str,
        is_available: bool,
        latitude=None,
        longitude=None,
    ):
        payload = {
            "full_name": full_name,
            "phone": "9000000000",
            "blood_group": blood_group,
            "gender": "male",
            "date_of_birth": "1995-01-01",
            "weight": 70,
            "city": "Delhi",
            "state": "Delhi",
        }

        if latitude is not None and longitude is not None:
            payload["latitude"] = latitude
            payload["longitude"] = longitude

        response = client.post(
            "/donor/profile",
            headers=headers,
            json=payload,
        )
        self.assertEqual(response.status_code, 201, response.text)
        donor = response.json()

        if not is_available:
            update_response = client.patch(
                "/donor/profile",
                headers=headers,
                json={"is_available": False},
            )
            self.assertEqual(update_response.status_code, 200, update_response.text)
            donor = update_response.json()

        return donor

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
        self.assertEqual(
            requester_profile_response.status_code, 201, requester_profile_response.text
        )

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
        self.assertEqual(
            blood_request_response.status_code, 201, blood_request_response.text
        )
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
        self.assertEqual(
            donor_profile_response.status_code, 201, donor_profile_response.text
        )

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
        self.assertEqual(
            proof_response.json()["proof_file"], "https://example.com/proof.jpg"
        )

        updated_requests_response = client.get(
            "/blood-request/me",
            headers=requester_headers,
        )
        self.assertEqual(
            updated_requests_response.status_code, 200, updated_requests_response.text
        )
        self.assertEqual(
            updated_requests_response.json()[0]["status"], "DONATION_IN_PROGRESS"
        )

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
        self.assertEqual(
            donor_profile_response.status_code, 201, donor_profile_response.text
        )

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
        self.assertEqual(
            blood_request_response.status_code, 201, blood_request_response.text
        )
        request_id = blood_request_response.json()["id"]

        volunteer_response = client.post(
            f"/volunteer/{request_id}", headers=donor_headers
        )
        self.assertEqual(volunteer_response.status_code, 201, volunteer_response.text)
        volunteer_id = volunteer_response.json()["id"]

        accept_response = client.patch(
            f"/volunteer/{volunteer_id}/accept", headers=requester_headers
        )
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

    def test_matching_returns_only_compatible_available_donors_ordered_by_distance(
        self,
    ):
        requester_token = self._create_user_and_login("requester.matching@test.com")
        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        self._create_requester_profile(requester_headers)
        blood_request = self._create_blood_request(requester_headers, blood_group="O+")
        request_id = blood_request["id"]

        donor_a_token = self._create_user_and_login("donor.a@test.com")
        donor_b_token = self._create_user_and_login("donor.b@test.com")
        donor_c_token = self._create_user_and_login("donor.c@test.com")
        donor_d_token = self._create_user_and_login("donor.d@test.com")

        donor_a = self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_a_token}"},
            full_name="Donor A",
            blood_group="O+",
            is_available=True,
            latitude=28.6140,
            longitude=77.2091,
        )
        donor_b = self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_b_token}"},
            full_name="Donor B",
            blood_group="O+",
            is_available=True,
            latitude=28.6500,
            longitude=77.2300,
        )
        self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_c_token}"},
            full_name="Donor C",
            blood_group="A+",
            is_available=True,
            latitude=28.6140,
            longitude=77.2091,
        )
        self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_d_token}"},
            full_name="Donor D",
            blood_group="O+",
            is_available=False,
            latitude=28.6140,
            longitude=77.2091,
        )

        matches_response = client.get(
            f"/blood-request/{request_id}/matches",
            headers=requester_headers,
        )
        self.assertEqual(matches_response.status_code, 200, matches_response.text)

        matches = matches_response.json()
        matched_names = [item["full_name"] for item in matches]

        self.assertIn("Donor A", matched_names)
        self.assertIn("Donor B", matched_names)
        self.assertNotIn("Donor C", matched_names)
        self.assertNotIn("Donor D", matched_names)

        self.assertEqual(matches[0]["donor_id"], donor_a["id"])
        self.assertEqual(matches[1]["donor_id"], donor_b["id"])
        self.assertLess(matches[0]["distance_km"], matches[1]["distance_km"])

    def test_matching_excludes_donor_without_location(self):
        requester_token = self._create_user_and_login("requester.nolocation@test.com")
        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        self._create_requester_profile(requester_headers)
        blood_request = self._create_blood_request(requester_headers, blood_group="O+")
        request_id = blood_request["id"]

        located_donor_token = self._create_user_and_login("donor.located@test.com")
        no_location_donor_token = self._create_user_and_login(
            "donor.nolocation@test.com"
        )

        located_donor = self._create_donor_profile(
            headers={"Authorization": f"Bearer {located_donor_token}"},
            full_name="Located Donor",
            blood_group="O+",
            is_available=True,
            latitude=28.6140,
            longitude=77.2091,
        )
        self._create_donor_profile(
            headers={"Authorization": f"Bearer {no_location_donor_token}"},
            full_name="No Location Donor",
            blood_group="O+",
            is_available=True,
        )

        matches_response = client.get(
            f"/blood-request/{request_id}/matches",
            headers=requester_headers,
        )
        self.assertEqual(matches_response.status_code, 200, matches_response.text)
        matches = matches_response.json()

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["donor_id"], located_donor["id"])

    def test_matching_returns_empty_when_no_compatible_available_donor(self):
        requester_token = self._create_user_and_login("requester.emptymatch@test.com")
        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        self._create_requester_profile(requester_headers)
        blood_request = self._create_blood_request(requester_headers, blood_group="AB-")
        request_id = blood_request["id"]

        donor_a_token = self._create_user_and_login("donor.empty.a@test.com")
        donor_b_token = self._create_user_and_login("donor.empty.b@test.com")

        self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_a_token}"},
            full_name="Unavailable O Donor",
            blood_group="O+",
            is_available=False,
            latitude=28.6140,
            longitude=77.2091,
        )
        self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_b_token}"},
            full_name="Available A Positive Donor",
            blood_group="A+",
            is_available=True,
            latitude=28.6140,
            longitude=77.2091,
        )

        matches_response = client.get(
            f"/blood-request/{request_id}/matches",
            headers=requester_headers,
        )
        self.assertEqual(matches_response.status_code, 200, matches_response.text)
        self.assertEqual(matches_response.json(), [])

    def test_matching_wrong_requester_gets_404(self):
        owner_token = self._create_user_and_login("requester.owner@test.com")
        other_token = self._create_user_and_login("requester.other@test.com")

        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        other_headers = {"Authorization": f"Bearer {other_token}"}

        self._create_requester_profile(owner_headers, full_name="Owner Requester")
        self._create_requester_profile(other_headers, full_name="Other Requester")

        blood_request = self._create_blood_request(owner_headers, blood_group="O+")
        request_id = blood_request["id"]

        matches_response = client.get(
            f"/blood-request/{request_id}/matches",
            headers=other_headers,
        )
        self.assertEqual(matches_response.status_code, 404, matches_response.text)
        self.assertEqual(matches_response.json()["detail"], "Blood request not found.")

    def test_matching_non_existent_request_gets_404(self):
        requester_token = self._create_user_and_login("requester.nonexistent@test.com")
        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        self._create_requester_profile(requester_headers)

        matches_response = client.get(
            "/blood-request/999999/matches",
            headers=requester_headers,
        )
        self.assertEqual(matches_response.status_code, 404, matches_response.text)
        self.assertEqual(matches_response.json()["detail"], "Blood request not found.")

    def test_matching_orders_nearest_to_farthest(self):
        requester_token = self._create_user_and_login("requester.ordering@test.com")
        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        self._create_requester_profile(requester_headers)
        blood_request = self._create_blood_request(requester_headers, blood_group="O+")
        request_id = blood_request["id"]

        donor_near_token = self._create_user_and_login("donor.near@test.com")
        donor_mid_token = self._create_user_and_login("donor.mid@test.com")
        donor_far_token = self._create_user_and_login("donor.far@test.com")

        donor_near = self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_near_token}"},
            full_name="Nearest Donor",
            blood_group="O+",
            is_available=True,
            latitude=28.6140,
            longitude=77.2091,
        )
        donor_mid = self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_mid_token}"},
            full_name="Middle Donor",
            blood_group="O+",
            is_available=True,
            latitude=28.6200,
            longitude=77.2150,
        )
        donor_far = self._create_donor_profile(
            headers={"Authorization": f"Bearer {donor_far_token}"},
            full_name="Farthest Donor",
            blood_group="O+",
            is_available=True,
            latitude=28.6500,
            longitude=77.2300,
        )

        matches_response = client.get(
            f"/blood-request/{request_id}/matches",
            headers=requester_headers,
        )
        self.assertEqual(matches_response.status_code, 200, matches_response.text)

        matches = matches_response.json()
        self.assertEqual(
            [item["donor_id"] for item in matches],
            [
                donor_near["id"],
                donor_mid["id"],
                donor_far["id"],
            ],
        )
        self.assertLess(matches[0]["distance_km"], matches[1]["distance_km"])
        self.assertLess(matches[1]["distance_km"], matches[2]["distance_km"])


if __name__ == "__main__":
    unittest.main()
