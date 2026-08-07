import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_state = {}
    for activity_name, activity in app_module.activities.items():
        original_state[activity_name] = {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": list(activity["participants"]),
        }

    yield

    for activity_name, activity in app_module.activities.items():
        restored = original_state[activity_name]
        activity["description"] = restored["description"]
        activity["schedule"] = restored["schedule"]
        activity["max_participants"] = restored["max_participants"]
        activity["participants"] = list(restored["participants"])


def test_get_activities_returns_non_cacheable_headers(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"


def test_signup_for_activity_adds_participant(client):
    activity_name = "Basketball Team"
    email = "student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    email = app_module.activities[activity_name]["participants"][0]

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}


def test_unregister_participant_removes_their_email(client):
    activity_name = "Chess Club"
    email = app_module.activities[activity_name]["participants"][0]

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_participant_returns_404_when_not_found(client):
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_signup_for_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown Activity/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
