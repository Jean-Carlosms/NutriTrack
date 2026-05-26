import json
from datetime import date, timedelta

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, session, url_for

from app.database import get_db
from app.models import ACTIVITY_LEVELS, GOALS, MEAL_TYPES, SEX_OPTIONS
from app.services.auth_service import (
    get_configured_username,
    is_auth_enabled,
    verify_credentials,
)
from app.services.backup_service import BackupError, create_sqlite_backup
from app.services.bodyfat_service import (
    calculate_bmi,
    calculate_us_navy_bodyfat,
    calculate_waist_height_ratio,
)
from app.services.calorie_service import calculate_calorie_plan
from app.services.export_service import (
    export_foods,
    export_meal_items,
    export_meals,
    export_measurements,
    export_weekly_report,
    export_weekly_reports_history,
)
from app.services.macro_service import calculate_food_amount, calculate_macro_targets
from app.services.progress_service import build_weekly_summary
from app.services.report_service import (
    WeeklyReportExistsError,
    build_weekly_report_snapshot,
    delete_weekly_report,
    get_weekly_report,
    get_weekly_report_by_id,
    list_weekly_reports,
    save_weekly_report,
)
from app.services.trend_service import build_trend_analysis

bp = Blueprint("main", __name__)


@bp.before_request
def require_login_when_enabled():
    if not is_auth_enabled():
        return None
    if request.endpoint in {"main.login", "main.logout"}:
        return None
    if session.get("nutritrack_authenticated"):
        return None

    next_path = request.full_path.rstrip("?")
    return redirect(url_for("main.login", next=next_path))


@bp.app_context_processor
def inject_auth_context():
    return {
        "auth_enabled": is_auth_enabled(),
        "auth_logged_in": bool(session.get("nutritrack_authenticated")),
        "auth_username": get_configured_username(),
    }


@bp.route("/login", methods=["GET", "POST"])
def login():
    if not is_auth_enabled():
        return redirect(url_for("main.dashboard"))

    next_path = safe_next_path(request.values.get("next"))
    if session.get("nutritrack_authenticated"):
        return redirect(next_path or url_for("main.dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if verify_credentials(username, password):
            session.clear()
            session["nutritrack_authenticated"] = True
            flash("Login realizado com sucesso.", "success")
            return redirect(next_path or url_for("main.dashboard"))

        flash("Usuario ou senha invalidos.", "warning")
        return render_template("login.html", next_path=next_path, username=username), 401

    return render_template("login.html", next_path=next_path, username="")


@bp.route("/logout")
def logout():
    session.clear()
    if is_auth_enabled():
        flash("Sessao encerrada.", "success")
        return redirect(url_for("main.login"))
    return redirect(url_for("main.dashboard"))


@bp.route("/")
def dashboard():
    db = get_db()
    profile = get_profile(db)
    today = date.today().isoformat()
    daily_total = get_daily_total(db, today)
    measurements = get_measurements(db, limit=30)
    daily_series = get_daily_totals(db, days=14)
    measurement_dicts = [dict(row) for row in measurements]
    latest_measurement = measurements[-1] if measurements else None
    previous_measurement = measurements[-2] if len(measurements) >= 2 else None
    weight_delta = None
    if latest_measurement and previous_measurement:
        weight_delta = round(
            latest_measurement["weight_kg"] - previous_measurement["weight_kg"],
            2,
        )

    calorie_plan = None
    macro_targets = None
    adherence_percent = None
    weekly_summary = None
    meals_summary = None
    if profile:
        calorie_plan = calculate_calorie_plan(profile)
        macro_targets = calculate_macro_targets(
            profile["current_weight_kg"],
            calorie_plan["target_calories"],
            profile["goal"],
        )
        if calorie_plan["target_calories"] > 0:
            adherence_percent = round(
                daily_total["calories"] / calorie_plan["target_calories"] * 100, 1
            )
        weekly_summary = build_weekly_summary(
            daily_totals=[dict(row) for row in get_daily_totals(db, days=7)],
            measurements=measurement_dicts[-7:],
            calorie_target=calorie_plan["target_calories"],
            macro_targets=macro_targets,
            goal=profile["goal"],
        )
        meals_summary = {
            "avg_calories": weekly_summary["avg_calories"],
            "target_calories": calorie_plan["target_calories"],
            "adherence_score": weekly_summary["adherence"]["score"],
        }

    trend_analysis = build_trend_analysis(measurement_dicts, meals_summary)

    chart_data = build_chart_data(measurements, daily_series, trend_analysis)
    return render_template(
        "dashboard.html",
        profile=profile,
        latest_measurement=latest_measurement,
        weight_delta=weight_delta,
        daily_total=daily_total,
        calorie_plan=calorie_plan,
        macro_targets=macro_targets,
        adherence_percent=adherence_percent,
        weekly_summary=weekly_summary,
        trend_analysis=trend_analysis,
        has_measurements=len(measurements) >= 2,
        has_meal_logs=any(day["calories"] > 0 for day in daily_series),
        chart_data=json.dumps(chart_data),
    )


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    db = get_db()
    if request.method == "POST":
        data, errors, values = profile_form_data(request.form)
        if errors:
            flash_form_errors(errors)
            return render_profile_form(values), 400

        db.execute(
            """
            INSERT INTO profiles
                (id, name, age, sex, height_cm, current_weight_kg, target_weight_kg,
                 activity_level, goal)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                age = excluded.age,
                sex = excluded.sex,
                height_cm = excluded.height_cm,
                current_weight_kg = excluded.current_weight_kg,
                target_weight_kg = excluded.target_weight_kg,
                activity_level = excluded.activity_level,
                goal = excluded.goal,
                updated_at = CURRENT_TIMESTAMP
            """,
            data,
        )
        db.commit()
        flash("Perfil salvo com sucesso.", "success")
        return redirect(url_for("main.dashboard"))

    return render_profile_form(get_profile(db))


@bp.route("/foods", methods=["GET", "POST"])
def foods():
    db = get_db()
    if request.method == "POST":
        data, errors, values = food_form_data(request.form)
        if errors:
            flash_form_errors(errors)
            foods_list = db.execute("SELECT * FROM foods ORDER BY name").fetchall()
            return render_template("foods.html", foods=foods_list, food=values), 400

        db.execute(
            """
            INSERT INTO foods
                (name, portion_grams, calories, protein_g, carbs_g, fat_g, fiber_g)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            data,
        )
        db.commit()
        flash("Alimento cadastrado.", "success")
        return redirect(url_for("main.foods"))

    foods_list = db.execute("SELECT * FROM foods ORDER BY name").fetchall()
    return render_template("foods.html", foods=foods_list, food=None)


@bp.route("/foods/<int:food_id>/edit", methods=["GET", "POST"])
def edit_food(food_id):
    db = get_db()
    food = db.execute("SELECT * FROM foods WHERE id = ?", (food_id,)).fetchone()
    if not food:
        flash("Alimento nao encontrado.", "warning")
        return redirect(url_for("main.foods"))

    if request.method == "POST":
        data, errors, values = food_form_data(request.form)
        if errors:
            flash_form_errors(errors)
            foods_list = db.execute("SELECT * FROM foods ORDER BY name").fetchall()
            return render_template(
                "foods.html",
                foods=foods_list,
                food={**dict(food), **values},
            ), 400

        db.execute(
            """
            UPDATE foods
            SET name = ?, portion_grams = ?, calories = ?, protein_g = ?,
                carbs_g = ?, fat_g = ?, fiber_g = ?
            WHERE id = ?
            """,
            (*data, food_id),
        )
        db.commit()
        flash("Alimento atualizado.", "success")
        return redirect(url_for("main.foods"))

    foods_list = db.execute("SELECT * FROM foods ORDER BY name").fetchall()
    return render_template("foods.html", foods=foods_list, food=food)


@bp.post("/foods/<int:food_id>/delete")
def delete_food(food_id):
    db = get_db()
    usage_count = db.execute(
        "SELECT COUNT(*) FROM meal_items WHERE food_id = ?",
        (food_id,),
    ).fetchone()[0]
    if usage_count:
        flash("Este alimento esta em refeicoes registradas e nao pode ser excluido.", "warning")
        return redirect(url_for("main.foods"))

    db.execute("DELETE FROM foods WHERE id = ?", (food_id,))
    db.commit()
    flash("Alimento removido.", "success")
    return redirect(url_for("main.foods"))


@bp.route("/meals", methods=["GET", "POST"])
def meals():
    db = get_db()
    if request.method == "POST":
        data, errors = meal_form_data(request.form, db)
        if errors:
            flash_form_errors(errors)
            selected_date = request.form.get("meal_date") or date.today().isoformat()
            return render_meals_page(db, selected_date), 400

        meal_date, meal_type, food_id, quantity_grams = data

        db.execute(
            """
            INSERT OR IGNORE INTO meals (meal_date, meal_type)
            VALUES (?, ?)
            """,
            (meal_date, meal_type),
        )
        meal = db.execute(
            "SELECT id FROM meals WHERE meal_date = ? AND meal_type = ?",
            (meal_date, meal_type),
        ).fetchone()
        db.execute(
            """
            INSERT INTO meal_items (meal_id, food_id, quantity_grams)
            VALUES (?, ?, ?)
            """,
            (meal["id"], food_id, quantity_grams),
        )
        db.commit()
        flash("Refeicao registrada.", "success")
        return redirect(url_for("main.meals", meal_date=meal_date))

    selected_date = request.args.get("meal_date", date.today().isoformat())
    return render_meals_page(db, selected_date)


@bp.post("/meal-items/<int:item_id>/delete")
def delete_meal_item(item_id):
    db = get_db()
    item = db.execute(
        """
        SELECT m.meal_date
        FROM meal_items mi
        JOIN meals m ON m.id = mi.meal_id
        WHERE mi.id = ?
        """,
        (item_id,),
    ).fetchone()
    db.execute("DELETE FROM meal_items WHERE id = ?", (item_id,))
    db.commit()
    flash("Item removido.", "success")
    return redirect(url_for("main.meals", meal_date=item["meal_date"] if item else None))


@bp.post("/meal-items/<int:item_id>/edit")
def edit_meal_item(item_id):
    db = get_db()
    item = db.execute(
        """
        SELECT mi.id, m.meal_date
        FROM meal_items mi
        JOIN meals m ON m.id = mi.meal_id
        WHERE mi.id = ?
        """,
        (item_id,),
    ).fetchone()
    if not item:
        flash("Item de refeicao nao encontrado.", "warning")
        return redirect(url_for("main.meals"))

    errors = []
    quantity_grams = parse_float(
        request.form,
        "quantity_grams",
        "Quantidade consumida",
        errors,
        min_value=0,
        strict_min=True,
    )
    if errors:
        flash_form_errors(errors)
        return redirect(url_for("main.meals", meal_date=item["meal_date"]))

    db.execute(
        "UPDATE meal_items SET quantity_grams = ? WHERE id = ?",
        (quantity_grams, item_id),
    )
    db.commit()
    flash("Quantidade atualizada.", "success")
    return redirect(url_for("main.meals", meal_date=item["meal_date"]))


@bp.route("/measurements", methods=["GET", "POST"])
def measurements():
    db = get_db()
    if request.method == "POST":
        data, errors, values = measurement_form_data(request.form)
        if errors:
            flash_form_errors(errors)
            return render_measurements_page(db, measurement=values), 400

        db.execute(
            """
            INSERT INTO measurements
                (measurement_date, weight_kg, waist_navel_cm, waist_min_cm,
                 abdomen_cm, chest_cm, hip_cm, right_arm_cm, left_arm_cm,
                 right_thigh_cm, left_thigh_cm, neck_cm, calf_cm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            data,
        )
        db.commit()
        flash("Medidas registradas.", "success")
        return redirect(url_for("main.measurements"))

    return render_measurements_page(db)


@bp.route("/measurements/<int:measurement_id>/edit", methods=["GET", "POST"])
def edit_measurement(measurement_id):
    db = get_db()
    measurement = get_measurement(db, measurement_id)
    if not measurement:
        flash("Medida nao encontrada.", "warning")
        return redirect(url_for("main.measurements"))

    if request.method == "POST":
        data, errors, values = measurement_form_data(request.form)
        if errors:
            flash_form_errors(errors)
            values["id"] = measurement_id
            return render_measurements_page(db, measurement=values), 400

        db.execute(
            """
            UPDATE measurements
            SET measurement_date = ?, weight_kg = ?, waist_navel_cm = ?,
                waist_min_cm = ?, abdomen_cm = ?, chest_cm = ?, hip_cm = ?,
                right_arm_cm = ?, left_arm_cm = ?, right_thigh_cm = ?,
                left_thigh_cm = ?, neck_cm = ?, calf_cm = ?
            WHERE id = ?
            """,
            (*data, measurement_id),
        )
        db.commit()
        flash("Medida atualizada.", "success")
        return redirect(url_for("main.measurements"))

    return render_measurements_page(db, measurement=measurement)


@bp.post("/measurements/<int:measurement_id>/delete")
def delete_measurement(measurement_id):
    db = get_db()
    measurement = get_measurement(db, measurement_id)
    if not measurement:
        flash("Medida nao encontrada.", "warning")
        return redirect(url_for("main.measurements"))

    db.execute("DELETE FROM measurements WHERE id = ?", (measurement_id,))
    db.commit()
    flash("Medida removida.", "success")
    return redirect(url_for("main.measurements"))


@bp.route("/weekly-report")
def weekly_report():
    db = get_db()
    profile_row = get_profile(db)
    if not profile_row:
        flash("Cadastre seu perfil para gerar o relatorio semanal.", "warning")
        return redirect(url_for("main.profile"))

    start = parse_week_start(request.args.get("week_start"))
    end = start + timedelta(days=6)
    calorie_plan, macro_targets, summary = build_weekly_context(db, profile_row, start, end)
    trend_analysis = build_trend_analysis_for_period(db, start, end, summary, calorie_plan)
    saved_report = get_weekly_report(db, start.isoformat())
    return render_template(
        "weekly_report.html",
        start=start,
        end=end,
        profile=profile_row,
        calorie_plan=calorie_plan,
        macro_targets=macro_targets,
        summary=summary,
        trend_analysis=trend_analysis,
        saved_report=saved_report,
    )


@bp.post("/weekly-report/save")
def save_weekly_report_route():
    return persist_weekly_report(overwrite=False)


@bp.post("/weekly-report/overwrite")
def overwrite_weekly_report_route():
    return persist_weekly_report(overwrite=True)


@bp.route("/weekly-reports")
def weekly_reports_history():
    db = get_db()
    reports = list_weekly_reports(db)
    return render_template("weekly_reports_history.html", reports=reports)


@bp.route("/weekly-reports/<int:report_id>")
def weekly_report_saved(report_id):
    db = get_db()
    report = get_weekly_report_by_id(db, report_id)
    if not report:
        flash("Relatorio salvo nao encontrado.", "warning")
        return redirect(url_for("main.weekly_reports_history"))
    return render_template("weekly_report_saved.html", report=report)


@bp.post("/weekly-reports/<int:report_id>/delete")
def delete_weekly_report_route(report_id):
    db = get_db()
    report = get_weekly_report_by_id(db, report_id)
    if not report:
        flash("Relatorio salvo nao encontrado.", "warning")
    else:
        delete_weekly_report(db, report_id)
        flash("Relatorio salvo removido.", "success")
    return redirect(url_for("main.weekly_reports_history"))


@bp.route("/exports")
def exports():
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    default_start = today - timedelta(days=30)
    return render_template(
        "exports.html",
        start_date=request.args.get("start_date", default_start.isoformat()),
        end_date=request.args.get("end_date", today.isoformat()),
        week_start=request.args.get("week_start", week_start.isoformat()),
    )


@bp.route("/exports/foods.csv")
def export_foods_csv():
    db = get_db()
    rows = db.execute("SELECT * FROM foods ORDER BY name").fetchall()
    return csv_response(export_foods(rows), "nutritrack_alimentos.csv")


@bp.route("/exports/meals.csv")
def export_meals_csv():
    db = get_db()
    start, end = parse_date_range(request.args.get("start_date"), request.args.get("end_date"))
    rows = db.execute(
        """
        SELECT id, meal_date, meal_type
        FROM meals
        WHERE meal_date BETWEEN ? AND ?
        ORDER BY meal_date, meal_type
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return csv_response(export_meals(rows), "nutritrack_refeicoes.csv")


@bp.route("/exports/meal-items.csv")
def export_meal_items_csv():
    db = get_db()
    start, end = parse_date_range(request.args.get("start_date"), request.args.get("end_date"))
    rows = get_meal_item_export_rows(db, start, end)
    return csv_response(export_meal_items(rows), "nutritrack_itens_refeicao.csv")


@bp.route("/exports/measurements.csv")
def export_measurements_csv():
    db = get_db()
    start, end = parse_date_range(request.args.get("start_date"), request.args.get("end_date"))
    rows = db.execute(
        """
        SELECT * FROM measurements
        WHERE measurement_date BETWEEN ? AND ?
        ORDER BY measurement_date, id
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return csv_response(export_measurements(rows), "nutritrack_medidas.csv")


@bp.route("/exports/weekly-report.csv")
def export_weekly_report_csv():
    db = get_db()
    profile_row = get_profile(db)
    start = parse_week_start(request.args.get("week_start"))
    end = start + timedelta(days=6)

    if not profile_row:
        summary = empty_weekly_summary("Cadastre um perfil para gerar o relatorio semanal.")
    else:
        summary = build_weekly_summary_for_period(db, profile_row, start, end)

    return csv_response(export_weekly_report(start, end, summary), "nutritrack_relatorio_semanal.csv")


@bp.route("/exports/weekly-reports-history.csv")
def export_weekly_reports_history_csv():
    db = get_db()
    reports = list_weekly_reports(db)
    return csv_response(
        export_weekly_reports_history(reports),
        "nutritrack_historico_relatorios_semanais.csv",
    )


@bp.route("/backup/create")
def create_backup():
    try:
        backup_path = create_sqlite_backup(current_app.config["DATABASE"])
    except BackupError as error:
        flash(str(error), "warning")
    else:
        flash(f"Backup criado: {backup_path.name}", "success")
    return redirect(url_for("main.exports"))


def get_profile(db):
    return db.execute("SELECT * FROM profiles WHERE id = 1").fetchone()


def persist_weekly_report(overwrite=False):
    db = get_db()
    profile_row = get_profile(db)
    if not profile_row:
        flash("Cadastre seu perfil para salvar relatorios semanais.", "warning")
        return redirect(url_for("main.profile"))

    start = parse_week_start(request.form.get("week_start") or request.args.get("week_start"))
    end = start + timedelta(days=6)
    calorie_plan, macro_targets, summary = build_weekly_context(db, profile_row, start, end)
    trend_analysis = build_trend_analysis_for_period(db, start, end, summary, calorie_plan)
    snapshot = build_weekly_report_snapshot(
        start,
        end,
        summary,
        trend_analysis,
        notes=(request.form.get("notes") or "").strip(),
    )
    try:
        report = save_weekly_report(db, snapshot, overwrite=overwrite)
    except WeeklyReportExistsError as error:
        flash(str(error), "warning")
        return redirect(url_for("main.weekly_report", week_start=start.isoformat()))

    message = "Relatorio semanal atualizado." if overwrite else "Relatorio semanal salvo."
    flash(message, "success")
    return redirect(url_for("main.weekly_report_saved", report_id=report["id"]))


def build_weekly_context(db, profile_row, start, end):
    calorie_plan = calculate_calorie_plan(profile_row)
    macro_targets = calculate_macro_targets(
        profile_row["current_weight_kg"],
        calorie_plan["target_calories"],
        profile_row["goal"],
    )
    summary = build_weekly_summary_for_period(db, profile_row, start, end, calorie_plan, macro_targets)
    return calorie_plan, macro_targets, summary


def build_weekly_summary_for_period(db, profile_row, start, end, calorie_plan=None, macro_targets=None):
    calorie_plan = calorie_plan or calculate_calorie_plan(profile_row)
    macro_targets = macro_targets or calculate_macro_targets(
        profile_row["current_weight_kg"],
        calorie_plan["target_calories"],
        profile_row["goal"],
    )
    daily_totals = get_daily_totals_between(db, start, end)
    week_measurements = db.execute(
        """
        SELECT * FROM measurements
        WHERE measurement_date BETWEEN ? AND ?
        ORDER BY measurement_date
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return build_weekly_summary(
        daily_totals=[dict(row) for row in daily_totals],
        measurements=[dict(row) for row in week_measurements],
        calorie_target=calorie_plan["target_calories"],
        macro_targets=macro_targets,
        goal=profile_row["goal"],
    )


def build_trend_analysis_for_period(db, start, end, summary, calorie_plan):
    measurements = db.execute(
        """
        SELECT * FROM measurements
        WHERE measurement_date BETWEEN ? AND ?
        ORDER BY measurement_date
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    meals_summary = {
        "avg_calories": summary["avg_calories"],
        "target_calories": calorie_plan["target_calories"],
        "adherence_score": summary["adherence"]["score"],
    }
    return build_trend_analysis([dict(row) for row in measurements], meals_summary)


def empty_weekly_summary(observation):
    return {
        "weight_start": None,
        "weight_end": None,
        "weight_delta": None,
        "avg_calories": 0,
        "avg_protein_g": 0,
        "avg_carbs_g": 0,
        "avg_fat_g": 0,
        "waist_delta": None,
        "adherence": {
            "score": 0,
            "classification": "baixa",
            "components": {"calories": 0, "protein": 0, "consistency": 0, "progress": 0},
        },
        "observation": observation,
    }


def profile_form_data(form):
    errors = []
    values = {
        "name": (form.get("name") or "").strip(),
        "age": parse_int(form, "age", "Idade", errors, min_value=1),
        "sex": form.get("sex"),
        "height_cm": parse_float(form, "height_cm", "Altura", errors, min_value=0, strict_min=True),
        "current_weight_kg": parse_float(
            form, "current_weight_kg", "Peso atual", errors, min_value=0, strict_min=True
        ),
        "target_weight_kg": parse_float(
            form, "target_weight_kg", "Peso meta", errors, min_value=0, strict_min=True
        ),
        "activity_level": form.get("activity_level"),
        "goal": form.get("goal"),
    }
    if not values["name"]:
        errors.append("Informe o nome.")
    if values["sex"] not in SEX_OPTIONS:
        errors.append("Selecione um sexo valido.")
    if values["activity_level"] not in ACTIVITY_LEVELS:
        errors.append("Selecione um nivel de atividade valido.")
    if values["goal"] not in GOALS:
        errors.append("Selecione um objetivo valido.")

    data = (
        values["name"],
        values["age"],
        values["sex"],
        values["height_cm"],
        values["current_weight_kg"],
        values["target_weight_kg"],
        values["activity_level"],
        values["goal"],
    )
    return data, errors, values


def food_form_data(form):
    errors = []
    values = {
        "name": (form.get("name") or "").strip(),
        "portion_grams": parse_float(
            form, "portion_grams", "Porcao", errors, min_value=0, strict_min=True
        ),
        "calories": parse_float(form, "calories", "Calorias", errors, min_value=0),
        "protein_g": parse_float(form, "protein_g", "Proteina", errors, min_value=0),
        "carbs_g": parse_float(form, "carbs_g", "Carboidratos", errors, min_value=0),
        "fat_g": parse_float(form, "fat_g", "Gorduras", errors, min_value=0),
        "fiber_g": parse_float(form, "fiber_g", "Fibras", errors, min_value=0, required=False) or 0,
    }
    if not values["name"]:
        errors.append("Informe o nome do alimento.")

    data = (
        values["name"],
        values["portion_grams"],
        values["calories"],
        values["protein_g"],
        values["carbs_g"],
        values["fat_g"],
        values["fiber_g"],
    )
    return data, errors, values


def meal_form_data(form, db):
    errors = []
    meal_date = parse_date(form.get("meal_date"), "Data", errors)
    meal_type = form.get("meal_type")
    food_id = parse_int(form, "food_id", "Alimento", errors, min_value=1)
    quantity_grams = parse_float(
        form, "quantity_grams", "Quantidade consumida", errors, min_value=0, strict_min=True
    )

    if meal_type not in MEAL_TYPES:
        errors.append("Selecione um tipo de refeicao valido.")
    if food_id is not None:
        food = db.execute("SELECT id FROM foods WHERE id = ?", (food_id,)).fetchone()
        if not food:
            errors.append("Selecione um alimento cadastrado.")

    return (meal_date, meal_type, food_id, quantity_grams), errors


def measurement_form_data(form):
    errors = []
    values_by_field = {}
    fields = [
        "measurement_date",
        "weight_kg",
        "waist_navel_cm",
        "waist_min_cm",
        "abdomen_cm",
        "chest_cm",
        "hip_cm",
        "right_arm_cm",
        "left_arm_cm",
        "right_thigh_cm",
        "left_thigh_cm",
        "neck_cm",
        "calf_cm",
    ]
    values = []
    for field in fields:
        value = form.get(field)
        if field == "measurement_date":
            parsed_value = parse_date(value, "Data", errors)
        elif field == "weight_kg":
            parsed_value = parse_float(form, field, "Peso", errors, min_value=0, strict_min=True)
        else:
            parsed_value = parse_float(form, field, measurement_label(field), errors, min_value=0, required=False)
        values.append(parsed_value)
        values_by_field[field] = parsed_value if parsed_value is not None else value
    return tuple(values), errors, values_by_field


def parse_float(form, field, label, errors, min_value=None, strict_min=False, required=True):
    raw_value = form.get(field)
    if raw_value in (None, ""):
        if required:
            errors.append(f"{label} e obrigatorio.")
        return None

    try:
        value = float(raw_value)
    except ValueError:
        errors.append(f"{label} deve ser um numero valido.")
        return None

    if min_value is not None:
        if strict_min and value <= min_value:
            errors.append(f"{label} deve ser maior que {min_value}.")
        elif not strict_min and value < min_value:
            errors.append(f"{label} nao pode ser negativo.")
    return value


def parse_int(form, field, label, errors, min_value=None):
    raw_value = form.get(field)
    if raw_value in (None, ""):
        errors.append(f"{label} e obrigatorio.")
        return None

    try:
        value = int(raw_value)
    except ValueError:
        errors.append(f"{label} deve ser um numero inteiro valido.")
        return None

    if min_value is not None and value < min_value:
        errors.append(f"{label} deve ser maior ou igual a {min_value}.")
    return value


def parse_date(raw_value, label, errors):
    if not raw_value:
        errors.append(f"{label} e obrigatoria.")
        return None
    try:
        date.fromisoformat(raw_value)
    except ValueError:
        errors.append(f"{label} deve ser uma data valida.")
        return None
    return raw_value


def measurement_label(field):
    labels = {
        "waist_navel_cm": "Cintura na altura do umbigo",
        "waist_min_cm": "Cintura mais fina",
        "abdomen_cm": "Abdomen",
        "chest_cm": "Peito",
        "hip_cm": "Quadril",
        "right_arm_cm": "Braco direito",
        "left_arm_cm": "Braco esquerdo",
        "right_thigh_cm": "Coxa direita",
        "left_thigh_cm": "Coxa esquerda",
        "neck_cm": "Pescoco",
        "calf_cm": "Panturrilha",
    }
    return labels.get(field, field)


def flash_form_errors(errors):
    for error in errors:
        flash(error, "warning")


def render_profile_form(profile_row):
    return render_template(
        "profile.html",
        profile=profile_row,
        activity_levels=ACTIVITY_LEVELS,
        goals=GOALS,
        sex_options=SEX_OPTIONS,
    )


def render_meals_page(db, selected_date):
    if not selected_date:
        selected_date = date.today().isoformat()
    foods_list = db.execute("SELECT * FROM foods ORDER BY name").fetchall()
    items = get_meal_items(db, selected_date)
    total = get_daily_total(db, selected_date)
    return render_template(
        "meals.html",
        foods=foods_list,
        meal_types=MEAL_TYPES,
        selected_date=selected_date,
        items=items,
        total=total,
    )


def render_measurements_page(db, measurement=None):
    profile_row = get_profile(db)
    rows = get_measurements(db, limit=50)
    latest = rows[-1] if rows else None
    estimates = build_body_estimates(profile_row, latest)
    return render_template(
        "measurements.html",
        measurements=rows,
        measurement=measurement,
        today=date.today().isoformat(),
        estimates=estimates,
    )


def get_measurement(db, measurement_id):
    return db.execute(
        "SELECT * FROM measurements WHERE id = ?",
        (measurement_id,),
    ).fetchone()


def get_measurements(db, limit):
    return db.execute(
        """
        SELECT * FROM (
            SELECT * FROM measurements
            ORDER BY measurement_date DESC, id DESC
            LIMIT ?
        ) ORDER BY measurement_date
        """,
        (limit,),
    ).fetchall()


def get_meal_items(db, selected_date):
    rows = db.execute(
        """
        SELECT mi.id, m.meal_date, m.meal_type, f.name, f.portion_grams,
               f.calories, f.protein_g, f.carbs_g, f.fat_g, f.fiber_g,
               mi.quantity_grams
        FROM meal_items mi
        JOIN meals m ON m.id = mi.meal_id
        JOIN foods f ON f.id = mi.food_id
        WHERE m.meal_date = ?
        ORDER BY m.meal_type, mi.id
        """,
        (selected_date,),
    ).fetchall()
    enriched = []
    for row in rows:
        item = dict(row)
        item.update(calculate_food_amount(row, row["quantity_grams"]))
        enriched.append(item)
    return enriched


def get_daily_total(db, selected_date):
    items = get_meal_items(db, selected_date)
    return sum_items(items)


def get_daily_totals(db, days):
    end = date.today()
    start = end - timedelta(days=days - 1)
    return get_daily_totals_between(db, start, end)


def get_daily_totals_between(db, start, end):
    rows = db.execute(
        """
        SELECT m.meal_date, f.portion_grams, f.calories, f.protein_g,
               f.carbs_g, f.fat_g, f.fiber_g, mi.quantity_grams
        FROM meal_items mi
        JOIN meals m ON m.id = mi.meal_id
        JOIN foods f ON f.id = mi.food_id
        WHERE m.meal_date BETWEEN ? AND ?
        ORDER BY m.meal_date
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()

    totals_by_date = {}
    for row in rows:
        amount = calculate_food_amount(row, row["quantity_grams"])
        current = totals_by_date.setdefault(row["meal_date"], empty_total(row["meal_date"]))
        for key in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]:
            current[key] += amount[key]

    series = []
    days = (end - start).days + 1
    for offset in range(days):
        day = (start + timedelta(days=offset)).isoformat()
        series.append(round_total(totals_by_date.get(day, empty_total(day))))
    return series


def parse_week_start(raw_value):
    if raw_value:
        try:
            parsed = date.fromisoformat(raw_value)
            return parsed - timedelta(days=parsed.weekday())
        except ValueError:
            flash("Semana invalida. Exibindo semana atual.", "warning")

    today = date.today()
    return today - timedelta(days=today.weekday())


def parse_date_range(start_raw, end_raw):
    today = date.today()
    start = safe_parse_date(start_raw) or (today - timedelta(days=30))
    end = safe_parse_date(end_raw) or today
    if start > end:
        start, end = end, start
    return start, end


def safe_parse_date(raw_value):
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        return None


def safe_next_path(raw_value):
    if not raw_value:
        return None
    if raw_value.startswith("/") and not raw_value.startswith("//"):
        return raw_value
    return None


def csv_response(csv_content, filename):
    response = Response(csv_content, mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def get_meal_item_export_rows(db, start, end):
    rows = db.execute(
        """
        SELECT mi.id, m.meal_date, m.meal_type, f.name AS food_name,
               f.portion_grams, f.calories, f.protein_g, f.carbs_g,
               f.fat_g, f.fiber_g, mi.quantity_grams
        FROM meal_items mi
        JOIN meals m ON m.id = mi.meal_id
        JOIN foods f ON f.id = mi.food_id
        WHERE m.meal_date BETWEEN ? AND ?
        ORDER BY m.meal_date, m.meal_type, mi.id
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    enriched = []
    for row in rows:
        item = dict(row)
        item.update(calculate_food_amount(row, row["quantity_grams"]))
        enriched.append(item)
    return enriched


def empty_total(day=None):
    total = {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "fiber_g": 0,
    }
    if day is not None:
        total["meal_date"] = day
    return total


def sum_items(items):
    total = empty_total()
    for item in items:
        for key in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]:
            total[key] += item[key]
    return round_total(total)


def round_total(total):
    return {
        key: (round(value, 1) if isinstance(value, (int, float)) else value)
        for key, value in total.items()
    }


def build_body_estimates(profile_row, latest):
    if not profile_row or not latest:
        return None

    estimates = {
        "educational_notice": "Estimativas educacionais, nao diagnostico medico.",
        "bmi": calculate_bmi(latest["weight_kg"], profile_row["height_cm"]),
    }
    if latest["waist_navel_cm"]:
        estimates["waist_height_ratio"] = calculate_waist_height_ratio(
            latest["waist_navel_cm"], profile_row["height_cm"]
        )
    if latest["waist_navel_cm"] and latest["neck_cm"]:
        try:
            estimates["us_navy_bodyfat"] = calculate_us_navy_bodyfat(
                profile_row["sex"],
                profile_row["height_cm"],
                latest["neck_cm"],
                latest["waist_navel_cm"],
                latest["hip_cm"],
            )
        except ValueError as error:
            estimates["us_navy_error"] = str(error)
    return estimates


def build_chart_data(measurements, daily_series, trend_analysis=None):
    moving_average = trend_analysis["moving_average"] if trend_analysis else []
    return {
        "weight": {
            "labels": [row["measurement_date"] for row in measurements],
            "values": [row["weight_kg"] for row in measurements],
            "movingAverage": [row["moving_average"] for row in moving_average],
        },
        "waist": {
            "labels": [row["measurement_date"] for row in measurements],
            "values": [row["waist_navel_cm"] for row in measurements],
        },
        "calories": {
            "labels": [row["meal_date"] for row in daily_series],
            "values": [row["calories"] for row in daily_series],
        },
        "macros": {
            "labels": [row["meal_date"] for row in daily_series],
            "protein": [row["protein_g"] for row in daily_series],
            "carbs": [row["carbs_g"] for row in daily_series],
            "fat": [row["fat_g"] for row in daily_series],
        },
    }
