"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    # Save original state
    original = {
        name: {**details, "participants": list(details["participants"])}
        for name, details in activities.items()
    }
    yield
    # Restore original state
    for name, details in original.items():
        activities[name]["participants"] = list(details["participants"])


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_fields(self, client):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert - each activity should have required fields
        for name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignupForActivity:
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        assert email in response.json()[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_registration_rejected(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterFromActivity:
    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already signed up

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        assert email not in response.json()[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_student_not_signed_up(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
