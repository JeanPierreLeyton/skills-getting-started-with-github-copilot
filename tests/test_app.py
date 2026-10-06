import src.app as app_module
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Chess Club": {
                "description": "Practice chess",
                "schedule": "Fridays",
                "max_participants": 4,
                "participants": ["existing@example.com"],
            },
            "Art Studio": {
                "description": "Make art",
                "schedule": "Wednesdays",
                "max_participants": 6,
                "participants": [],
            },
        },
    )
    return TestClient(app_module.app)


def test_get_activities_returns_current_activities(client):
    # Arrange
    expected_activities = app_module.activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert app_module.activities["Chess Club"]["participants"].count(email) == 1


def test_signup_requires_email(client):
    # Arrange
    activity_path = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(activity_path)

    # Assert
    assert response.status_code == 422


def test_remove_participant_unregisters_student(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_participant_rejects_unknown_activity(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_rejects_unregistered_student(client):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_remove_participant_requires_email(client):
    # Arrange
    activity_path = "/activities/Chess%20Club/signup"

    # Act
    response = client.delete(activity_path)

    # Assert
    assert response.status_code == 422


def test_root_redirects_to_static_index(client):
    # Arrange
    redirect_target = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == redirect_target


def test_static_index_is_available(client):
    # Arrange
    index_path = "/static/index.html"

    # Act
    response = client.get(index_path)

    # Assert
    assert response.status_code == 200
    assert "Mergington High School Activities" in response.text
