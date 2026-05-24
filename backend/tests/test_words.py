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
    # Collect IDs before closing the session to avoid detached instance errors
    word_ids = [w.id for w in test_words]
    db.close()
    return word_ids


def test_list_words_default_pagination(client, seed_words):
    response = client.get("/api/words")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["size"] == 50
    assert data["total"] >= 10
    assert len(data["items"]) >= 10


def test_list_words_search(client, seed_words):
    response = client.get("/api/words?search=abandon")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert any("abandon" in item["english"].lower() for item in data["items"])


def test_list_words_page2(client, seed_words):
    response = client.get("/api/words?page=2&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["items"]) <= 10


def test_get_single_word(client, seed_words):
    word_id = seed_words[0]
    response = client.get(f"/api/words/{word_id}")
    assert response.status_code == 200
    data = response.json()
    assert "english" in data
    assert "chinese" in data


def test_get_word_not_found(client, seed_words):
    response = client.get("/api/words/99999")
    assert response.status_code == 404
