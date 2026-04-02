def test_login_success(client):
    r = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin@123!"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    r = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "WrongPass!"},
    )
    assert r.status_code == 401
    assert "detail" in r.json()


def test_login_unknown_email(client):
    r = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "SomePass@123"},
    )
    assert r.status_code == 401


def test_login_invalid_email_format(client):
    r = client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "SomePass@123"},
    )
    assert r.status_code == 422


def test_protected_route_without_token(client):
    r = client.get("/users/me")
    assert r.status_code == 403


def test_protected_route_with_invalid_token(client):
    r = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert r.status_code == 401


def test_get_me(client, admin_headers):
    r = client.get("/users/me", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "admin@finance.local"
    assert data["role"] == "admin"