import pytest
from tests.conftest import get_test_db
from app.models.word import Word


@pytest.fixture
def seed_words():
    """Seed some test words into the test database."""
    db = get_test_db()
    test_words = [
        Word(english="abandon", chinese="放弃", part_of_speech="v.", difficulty_level=1),
        Word(english="ability", chinese="能力", part_of_speech="n.", difficulty_level=1),
    ]
    for w in test_words:
        db.add(w)
    db.commit()
    db.close()


def get_token(client, username="proguser"):
    client.post("/api/auth/register", json={
        "username": username, "email": f"{username}@test.com", "password": "pass123"
    })
    resp = client.post("/api/auth/login", json={"username": username, "password": "pass123"})
    return resp.json()["access_token"]


def test_progress_summary_empty(client):
    token = get_token(client)
    resp = client.get("/api/progress", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_words"] == 0


def test_update_progress_knew(client, seed_words):
    token = get_token(client)
    words = client.get("/api/words?size=1").json()
    word_id = words["items"][0]["id"]

    resp = client.put(
        f"/api/progress/{word_id}",
        json={"knew_it": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "learning"
    assert data["correct_count"] == 1


def test_update_progress_didnt_know(client, seed_words):
    token = get_token(client, "proguser2")
    words = client.get("/api/words?size=1").json()
    word_id = words["items"][0]["id"]

    client.put(
        f"/api/progress/{word_id}",
        json={"knew_it": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    resp = client.put(
        f"/api/progress/{word_id}",
        json={"knew_it": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "new"


def test_progress_unauthorized(client):
    resp = client.get("/api/progress")
    assert resp.status_code == 401
