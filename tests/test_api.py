import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: snapshot and restore the in-memory activities around each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    # Arrange (client ready)
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "tester@example.com"
    initial = len(activities[activity]["participants"])

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == initial + 1


def test_signup_duplicate_rejected():
    # Arrange
    activity = "Programming Class"
    email = "emma@mergington.edu"  # already signed up

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 400
    assert "already" in resp.json().get("detail", "").lower()


def test_remove_participant():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    initial = len(activities[activity]["participants"])

    # Act
    resp = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == initial - 1
