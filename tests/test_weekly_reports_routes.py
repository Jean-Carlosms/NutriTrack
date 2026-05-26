from tests.test_app import make_app, valid_measurement_payload, valid_profile_payload
from tests.test_auth import auth_config


def prepare_report_data(client):
    client.post("/profile", data=valid_profile_payload())
    payload = valid_measurement_payload()
    payload["measurement_date"] = "2026-05-25"
    payload["weight_kg"] = "80"
    client.post("/measurements", data=payload)
    payload["measurement_date"] = "2026-05-31"
    payload["weight_kg"] = "79.5"
    client.post("/measurements", data=payload)


def test_weekly_report_save_route_and_history():
    app = make_app()
    client = app.test_client()
    prepare_report_data(client)

    save_response = client.post(
        "/weekly-report/save",
        data={"week_start": "2026-05-25"},
        follow_redirects=True,
    )
    history_response = client.get("/weekly-reports")

    assert save_response.status_code == 200
    assert "Relatorio salvo" in save_response.get_data(as_text=True)
    assert history_response.status_code == 200
    assert "2026-05-25" in history_response.get_data(as_text=True)


def test_weekly_report_save_prevents_duplicate_and_overwrite_updates():
    app = make_app()
    client = app.test_client()
    prepare_report_data(client)
    client.post("/weekly-report/save", data={"week_start": "2026-05-25"})

    duplicate = client.post(
        "/weekly-report/save",
        data={"week_start": "2026-05-25"},
        follow_redirects=True,
    )
    overwrite = client.post(
        "/weekly-report/overwrite",
        data={"week_start": "2026-05-25"},
        follow_redirects=True,
    )

    assert "Ja existe relatorio salvo" in duplicate.get_data(as_text=True)
    assert overwrite.status_code == 200
    assert "Relatorio salvo" in overwrite.get_data(as_text=True)


def test_view_and_delete_saved_weekly_report():
    app = make_app()
    client = app.test_client()
    prepare_report_data(client)
    client.post("/weekly-report/save", data={"week_start": "2026-05-25"})

    with app.app_context():
        from app.database import get_db

        report = get_db().execute("SELECT id FROM weekly_reports LIMIT 1").fetchone()

    view_response = client.get(f"/weekly-reports/{report['id']}")
    delete_response = client.post(
        f"/weekly-reports/{report['id']}/delete",
        follow_redirects=True,
    )

    assert view_response.status_code == 200
    assert "Snapshot criado" in view_response.get_data(as_text=True)
    assert "Nenhum relatorio salvo ainda" in delete_response.get_data(as_text=True)


def test_export_weekly_reports_history_csv():
    app = make_app()
    client = app.test_client()
    prepare_report_data(client)
    client.post("/weekly-report/save", data={"week_start": "2026-05-25"})

    response = client.get("/exports/weekly-reports-history.csv")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "Content-Disposition" in response.headers
    assert body.startswith("week_start,week_end,created_at")
    assert "2026-05-25" in body


def test_weekly_report_dynamic_route_still_works():
    app = make_app()
    client = app.test_client()
    prepare_report_data(client)

    response = client.get("/weekly-report?week_start=2026-05-25")

    assert response.status_code == 200
    assert "Relatorio semanal" in response.get_data(as_text=True)


def test_auth_protects_saved_report_routes():
    app = make_app(auth_config())
    client = app.test_client()

    assert client.get("/weekly-reports").status_code == 302
    assert client.post("/weekly-report/save", data={"week_start": "2026-05-25"}).status_code == 302

    client.post("/login", data={"username": "admin", "password": "secret"})
    assert client.get("/weekly-reports").status_code == 200
