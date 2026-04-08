import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITY_PARTICIPANTS = {
    name: list(activity["participants"])
    for name, activity in activities.items()
}

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test
    for name, activity in activities.items():
        # Remove all participants except the initial ones
        activity["participants"] = list(INITIAL_ACTIVITY_PARTICIPANTS[name])


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_success():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    email = activities["Chess Club"]["participants"][0]
    activity = "Chess Club"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_success():
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered():
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]


def test_unregister_nonexistent_activity():
    response = client.delete("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
