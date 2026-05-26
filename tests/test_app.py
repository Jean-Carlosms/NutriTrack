from app import create_app


def make_app(config=None):
    app_config = {
        "TESTING": True,
        "DATABASE": ":memory:",
        "SECRET_KEY": "test-secret",
    }
    if config:
        app_config.update(config)
    return create_app(app_config)


def valid_profile_payload():
    return {
        "name": "Usuario Teste",
        "age": "30",
        "sex": "male",
        "height_cm": "180",
        "current_weight_kg": "80",
        "target_weight_kg": "75",
        "activity_level": "moderate",
        "goal": "fat_loss",
    }


def valid_food_payload():
    return {
        "name": "Iogurte teste",
        "portion_grams": "100",
        "calories": "90",
        "protein_g": "10",
        "carbs_g": "8",
        "fat_g": "2",
        "fiber_g": "0",
    }


def valid_measurement_payload():
    return {
        "measurement_date": "2026-05-25",
        "weight_kg": "80",
        "waist_navel_cm": "88",
        "waist_min_cm": "82",
        "abdomen_cm": "92",
        "chest_cm": "101",
        "hip_cm": "98",
        "right_arm_cm": "34",
        "left_arm_cm": "34",
        "right_thigh_cm": "57",
        "left_thigh_cm": "57",
        "neck_cm": "39",
        "calf_cm": "38",
    }


def test_create_app_and_smoke_routes():
    app = make_app()
    client = app.test_client()

    for path in ["/", "/profile", "/foods", "/meals", "/measurements", "/weekly-report"]:
        response = client.get(path)
        assert response.status_code in {200, 302}


def test_profile_validation_rejects_invalid_payload():
    app = make_app()
    client = app.test_client()

    response = client.post(
        "/profile",
        data={
            "name": "",
            "age": "0",
            "sex": "invalid",
            "height_cm": "0",
            "current_weight_kg": "-1",
            "target_weight_kg": "0",
            "activity_level": "unknown",
            "goal": "unknown",
        },
    )

    assert response.status_code == 400
    assert "Informe o nome" in response.get_data(as_text=True)


def test_valid_profile_post_redirects_to_dashboard():
    app = make_app()
    client = app.test_client()

    response = client.post("/profile", data=valid_profile_payload())

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_valid_food_post_creates_food():
    app = make_app()
    client = app.test_client()

    response = client.post("/foods", data=valid_food_payload(), follow_redirects=True)

    assert response.status_code == 200
    assert "Iogurte teste" in response.get_data(as_text=True)


def test_invalid_food_post_preserves_values():
    app = make_app()
    client = app.test_client()
    payload = valid_food_payload()
    payload["name"] = ""
    payload["calories"] = "-10"

    response = client.post("/foods", data=payload)
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Informe o nome do alimento" in body
    assert "Iogurte" not in body


def test_valid_measurement_post_creates_measurement():
    app = make_app()
    client = app.test_client()

    response = client.post("/measurements", data=valid_measurement_payload(), follow_redirects=True)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "2026-05-25" in body


def test_invalid_measurement_post_returns_error_and_preserves_form():
    app = make_app()
    client = app.test_client()
    payload = valid_measurement_payload()
    payload["weight_kg"] = "-1"

    response = client.post("/measurements", data=payload)
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Peso deve ser maior" in body
    assert "2026-05-25" in body


def test_edit_and_delete_measurement():
    app = make_app()
    client = app.test_client()
    client.post("/measurements", data=valid_measurement_payload())

    with app.app_context():
        from app.database import get_db

        measurement = get_db().execute(
            "SELECT * FROM measurements WHERE measurement_date = ?",
            ("2026-05-25",),
        ).fetchone()

    payload = valid_measurement_payload()
    payload["weight_kg"] = "79.5"
    edit_response = client.post(
        f"/measurements/{measurement['id']}/edit",
        data=payload,
        follow_redirects=True,
    )
    assert edit_response.status_code == 200
    assert "79.5 kg" in edit_response.get_data(as_text=True)

    delete_response = client.post(
        f"/measurements/{measurement['id']}/delete",
        follow_redirects=True,
    )
    assert delete_response.status_code == 200
    assert "2026-05-25" not in delete_response.get_data(as_text=True)


def test_create_edit_and_delete_meal_item():
    app = make_app()
    client = app.test_client()

    response = client.post(
        "/meals",
        data={
            "meal_date": "2026-05-25",
            "meal_type": "Almoco",
            "food_id": "1",
            "quantity_grams": "150",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert 'value="150.0"' in response.get_data(as_text=True)

    with app.app_context():
        from app.database import get_db

        item = get_db().execute("SELECT id FROM meal_items ORDER BY id DESC LIMIT 1").fetchone()

    edit_response = client.post(
        f"/meal-items/{item['id']}/edit",
        data={"quantity_grams": "200"},
        follow_redirects=True,
    )
    assert edit_response.status_code == 200
    assert 'value="200.0"' in edit_response.get_data(as_text=True)

    delete_response = client.post(
        f"/meal-items/{item['id']}/delete",
        follow_redirects=True,
    )
    assert delete_response.status_code == 200
    assert "Nenhuma refeicao registrada" in delete_response.get_data(as_text=True)


def test_dashboard_without_data_and_with_minimum_data():
    app = make_app()
    client = app.test_client()

    with app.app_context():
        from app.database import get_db

        db = get_db()
        db.execute("DELETE FROM meal_items")
        db.execute("DELETE FROM meals")
        db.execute("DELETE FROM measurements")
        db.execute("DELETE FROM profiles")
        db.commit()

    empty_response = client.get("/")
    empty_body = empty_response.get_data(as_text=True)
    assert empty_response.status_code == 200
    assert "Cadastre seu perfil" in empty_body

    client.post("/profile", data=valid_profile_payload())
    client.post("/measurements", data=valid_measurement_payload())
    second_measurement = valid_measurement_payload()
    second_measurement["measurement_date"] = "2026-05-26"
    second_measurement["weight_kg"] = "79.7"
    client.post("/measurements", data=second_measurement)
    client.post(
        "/meals",
        data={
            "meal_date": "2026-05-26",
            "meal_type": "Almoco",
            "food_id": "1",
            "quantity_grams": "100",
        },
    )

    full_response = client.get("/")
    full_body = full_response.get_data(as_text=True)
    assert full_response.status_code == 200
    assert "Score semanal" in full_body
    assert "79.7 kg" in full_body


def test_dashboard_renders_trend_analysis_with_little_data():
    app = make_app()
    client = app.test_client()
    with app.app_context():
        from app.database import get_db

        db = get_db()
        db.execute("DELETE FROM measurements")
        db.commit()

    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Analise de Tendencia" in body
    assert "dados insuficientes" in body


def test_dashboard_renders_trend_analysis_with_enough_data():
    app = make_app()
    client = app.test_client()
    with app.app_context():
        from app.database import get_db

        db = get_db()
        db.execute("DELETE FROM measurements")
        db.commit()
    client.post("/profile", data=valid_profile_payload())
    first = valid_measurement_payload()
    first["measurement_date"] = "2026-05-01"
    first["weight_kg"] = "80"
    second = valid_measurement_payload()
    second["measurement_date"] = "2026-05-15"
    second["weight_kg"] = "79"
    client.post("/measurements", data=first)
    client.post("/measurements", data=second)

    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "reduzindo" in body
    assert "Media movel atual" in body


def test_weekly_report_renders_trend_analysis():
    app = make_app()
    client = app.test_client()
    client.post("/profile", data=valid_profile_payload())
    client.post("/measurements", data=valid_measurement_payload())

    response = client.get("/weekly-report?week_start=2026-05-25")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Analise de tendencia da semana" in body
    assert "Possivel plato" in body
