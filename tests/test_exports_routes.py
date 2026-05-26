from tests.test_app import make_app, valid_measurement_payload, valid_profile_payload


def csv_text(response):
    return response.get_data(as_text=True)


def assert_csv_download(response, filename):
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "Content-Disposition" in response.headers
    assert filename in response.headers["Content-Disposition"]


def test_export_foods_route_returns_header_and_data():
    app = make_app()
    client = app.test_client()

    response = client.get("/exports/foods.csv")

    assert_csv_download(response, "nutritrack_alimentos.csv")
    body = csv_text(response)
    assert body.startswith("id,nome,porcao_gramas")
    assert "Arroz cozido" in body


def test_export_measurements_route_with_no_data_returns_header_only():
    app = make_app()
    client = app.test_client()
    with app.app_context():
        from app.database import get_db

        db = get_db()
        db.execute("DELETE FROM measurements")
        db.commit()

    response = client.get("/exports/measurements.csv")

    assert_csv_download(response, "nutritrack_medidas.csv")
    lines = csv_text(response).splitlines()
    assert lines[0].startswith("id,data,peso_kg")
    assert len(lines) == 1


def test_export_measurements_route_with_data():
    app = make_app()
    client = app.test_client()
    client.post("/measurements", data=valid_measurement_payload())

    response = client.get("/exports/measurements.csv?start_date=2026-05-01&end_date=2026-05-31")

    assert_csv_download(response, "nutritrack_medidas.csv")
    assert "2026-05-25" in csv_text(response)


def test_export_meals_and_meal_items_by_period():
    app = make_app()
    client = app.test_client()
    client.post(
        "/meals",
        data={
            "meal_date": "2026-05-25",
            "meal_type": "Almoco",
            "food_id": "1",
            "quantity_grams": "100",
        },
    )

    meals_response = client.get("/exports/meals.csv?start_date=2026-05-25&end_date=2026-05-25")
    items_response = client.get("/exports/meal-items.csv?start_date=2026-05-25&end_date=2026-05-25")

    assert_csv_download(meals_response, "nutritrack_refeicoes.csv")
    assert_csv_download(items_response, "nutritrack_itens_refeicao.csv")
    assert "Almoco" in csv_text(meals_response)
    assert "Arroz cozido" in csv_text(items_response)
    assert "128.0" in csv_text(items_response)


def test_export_weekly_report_route():
    app = make_app()
    client = app.test_client()
    client.post("/profile", data=valid_profile_payload())
    client.post("/measurements", data=valid_measurement_payload())

    response = client.get("/exports/weekly-report.csv?week_start=2026-05-25")

    assert_csv_download(response, "nutritrack_relatorio_semanal.csv")
    body = csv_text(response)
    assert body.startswith("semana_inicio,semana_fim")
    assert "2026-05-25" in body


def test_exports_page_smoke():
    app = make_app()
    client = app.test_client()

    response = client.get("/exports")

    assert response.status_code == 200
    assert "Exportacoes" in response.get_data(as_text=True)
