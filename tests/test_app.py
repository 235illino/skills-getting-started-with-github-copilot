from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def test_unregister_participant_removes_their_email():
    activity_name = "Chess Club"
    original_participants = list(app_module.activities[activity_name]["participants"])

    try:
        response = client.delete(f"/activities/{activity_name}/participants/{original_participants[0]}")

        assert response.status_code == 200
        assert original_participants[0] not in app_module.activities[activity_name]["participants"]
    finally:
        app_module.activities[activity_name]["participants"] = original_participants


def test_get_activities_returns_non_cacheable_headers():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
