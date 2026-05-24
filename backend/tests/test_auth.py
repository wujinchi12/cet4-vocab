def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "username": "dup", "email": "a@b.com", "password": "pass123"
    })
    response = client.post("/api/auth/register", json={
        "username": "dup", "email": "c@d.com", "password": "pass123"
    })
    assert response.status_code == 409


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "loginuser", "email": "login@test.com", "password": "mypassword"
    })
    response = client.post("/api/auth/login", json={
        "username": "loginuser", "password": "mypassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "wrong", "email": "wrong@test.com", "password": "correct"
    })
    response = client.post("/api/auth/login", json={
        "username": "wrong", "password": "incorrect"
    })
    assert response.status_code == 401
