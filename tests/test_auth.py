from werkzeug.security import generate_password_hash

from tests.test_app import make_app


def auth_config():
    return {
        "NUTRITRACK_AUTH_ENABLED": "true",
        "NUTRITRACK_USERNAME": "admin",
        "NUTRITRACK_PASSWORD_HASH": generate_password_hash("secret"),
    }


def test_auth_disabled_allows_dashboard_access():
    app = make_app({"NUTRITRACK_AUTH_ENABLED": "false"})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_auth_enabled_redirects_dashboard_to_login():
    app = make_app(auth_config())
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert "/login?next=/" in response.headers["Location"]


def test_login_page_is_accessible_when_auth_enabled():
    app = make_app(auth_config())
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert "Entrar no NutriTrack" in response.get_data(as_text=True)


def test_valid_login_authenticates_and_redirects_to_internal_next():
    app = make_app(auth_config())
    client = app.test_client()

    response = client.post(
        "/login?next=/foods",
        data={"username": "admin", "password": "secret"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/foods")
    assert client.get("/foods").status_code == 200


def test_invalid_login_does_not_authenticate():
    app = make_app(auth_config())
    client = app.test_client()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401
    assert "Usuario ou senha invalidos" in response.get_data(as_text=True)
    assert client.get("/").status_code == 302


def test_logout_clears_session():
    app = make_app(auth_config())
    client = app.test_client()
    client.post("/login", data={"username": "admin", "password": "secret"})

    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert client.get("/").status_code == 302


def test_csv_routes_are_protected_when_auth_enabled():
    app = make_app(auth_config())
    client = app.test_client()

    response = client.get("/exports/foods.csv")

    assert response.status_code == 302
    assert "/login?next=/exports/foods.csv" in response.headers["Location"]


def test_static_files_are_not_protected():
    app = make_app(auth_config())
    client = app.test_client()

    response = client.get("/static/css/style.css")

    assert response.status_code == 200


def test_external_next_is_ignored_after_login():
    app = make_app(auth_config())
    client = app.test_client()

    response = client.post(
        "/login?next=https://example.com",
        data={"username": "admin", "password": "secret"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert "example.com" not in response.headers["Location"]
