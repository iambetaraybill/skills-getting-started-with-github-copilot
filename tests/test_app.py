import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def test_activities(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 3,
            "participants": ["existing@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(test_activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, test_activities):
    # Arrange
    expected_activities = test_activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, test_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert test_activities[activity_name]["participants"] == [
        "existing@example.com",
        email,
    ]


def test_signup_rejects_duplicate_participant(client, test_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "existing@example.com"
    original_participants = test_activities[activity_name]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert test_activities[activity_name]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client, test_activities):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, test_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert test_activities[activity_name]["participants"] == []


def test_unregister_rejects_missing_participant(client, test_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@example.com"
    original_participants = test_activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert test_activities[activity_name]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(client, test_activities):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"