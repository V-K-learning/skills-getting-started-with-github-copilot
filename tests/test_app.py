import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function(function):
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    client.post(signup_url)

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_email():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "remove@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    delete_url = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    client.post(signup_url)

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_from_programming_class():
    # Arrange
    client = TestClient(app)
    activity_name = "Programming Class"
    email = "programmer@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    delete_url = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    client.post(signup_url)

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    delete_url = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
