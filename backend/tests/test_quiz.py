import pytest
from tests.conftest import get_test_db
from app.models.word import Word


@pytest.fixture
def seed_words(setup_db):
    """Seed some test words into the test database."""
    db = get_test_db()
    test_words = [
        Word(english="abandon", chinese="放弃", part_of_speech="v.", difficulty_level=1),
        Word(english="ability", chinese="能力", part_of_speech="n.", difficulty_level=1),
        Word(english="absent", chinese="缺席的", part_of_speech="adj.", difficulty_level=2),
        Word(english="absorb", chinese="吸收", part_of_speech="v.", difficulty_level=2),
        Word(english="abstract", chinese="抽象的", part_of_speech="adj.", difficulty_level=3),
        Word(english="abundant", chinese="丰富的", part_of_speech="adj.", difficulty_level=3),
        Word(english="academy", chinese="学院", part_of_speech="n.", difficulty_level=1),
        Word(english="accelerate", chinese="加速", part_of_speech="v.", difficulty_level=3),
        Word(english="accept", chinese="接受", part_of_speech="v.", difficulty_level=1),
        Word(english="access", chinese="进入", part_of_speech="n.", difficulty_level=2),
        Word(english="accident", chinese="事故", part_of_speech="n.", difficulty_level=1),
        Word(english="accompany", chinese="陪伴", part_of_speech="v.", difficulty_level=2),
    ]
    for w in test_words:
        db.add(w)
    db.commit()
    word_ids = [w.id for w in test_words]
    db.close()
    return word_ids


def get_token(client, username="quizuser"):
    client.post("/api/auth/register", json={
        "username": username, "email": f"{username}@test.com", "password": "pass123"
    })
    resp = client.post("/api/auth/login", json={"username": username, "password": "pass123"})
    return resp.json()["access_token"]


def test_generate_choice_quiz(client, seed_words):
    token = get_token(client)
    resp = client.post(
        "/api/quiz/generate",
        json={"quiz_type": "choice", "count": 5, "direction": "en_to_cn"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    for q in data:
        assert q["type"] == "choice"
        assert len(q["options"]) == 4
        assert "correct_answer" not in q


def test_generate_fill_quiz(client, seed_words):
    token = get_token(client)
    resp = client.post(
        "/api/quiz/generate",
        json={"quiz_type": "fill", "count": 3, "direction": "cn_to_en"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    for q in data:
        assert q["type"] == "fill"
        assert "correct_answer" not in q


def test_submit_quiz(client, seed_words):
    token = get_token(client, "quizuser2")
    # Use the internal API directly to get questions with correct answers
    from app.services.quiz_generator import generate_quiz_questions
    db = get_test_db()
    questions = generate_quiz_questions(db, "choice", 3, "en_to_cn")
    db.close()

    answers = [{"word_id": q["word_id"], "answer": q["correct_answer"], "correct_answer": q["correct_answer"]} for q in questions]
    resp = client.post(
        "/api/quiz/submit",
        json={"quiz_type": "choice", "answers": answers},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == 3
    assert data["correct_count"] == 3
    assert data["score_percent"] == 100.0


def test_quiz_history(client, seed_words):
    token = get_token(client, "quizuser3")
    resp = client.get("/api/quiz/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_quiz_unauthorized(client, seed_words):
    resp = client.post("/api/quiz/generate", json={"quiz_type": "choice", "count": 5})
    assert resp.status_code == 401
