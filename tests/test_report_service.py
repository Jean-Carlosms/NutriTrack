from datetime import date

import pytest

from app.database import get_db
from app.services.report_service import (
    WeeklyReportExistsError,
    build_weekly_report_snapshot,
    delete_weekly_report,
    get_weekly_report,
    list_weekly_reports,
    save_weekly_report,
)
from tests.test_app import make_app


def sample_summary(score=82):
    return {
        "weight_start": 80,
        "weight_end": 79.4,
        "weight_delta": -0.6,
        "avg_calories": 2000,
        "avg_protein_g": 150,
        "avg_carbs_g": 210,
        "avg_fat_g": 60,
        "waist_delta": -1,
        "adherence": {"score": score},
    }


def sample_trend(recommendation="Manter estrategia atual."):
    return {
        "trend": {"classification": "reduzindo"},
        "weekly_delta": -0.6,
        "latest_moving_average": 79.6,
        "plateau": {"plateau_detected": False},
        "recommendation": recommendation,
    }


def sample_snapshot(score=82, recommendation="Manter estrategia atual."):
    return build_weekly_report_snapshot(
        date(2026, 5, 25),
        date(2026, 5, 31),
        sample_summary(score),
        sample_trend(recommendation),
    )


def test_weekly_reports_table_has_expected_columns():
    app = make_app()
    with app.app_context():
        columns = {
            row["name"]
            for row in get_db().execute("PRAGMA table_info(weekly_reports)").fetchall()
        }

    assert "week_start" in columns
    assert "avg_calories" in columns
    assert "trend_status" in columns
    assert "recommendation" in columns


def test_save_weekly_report_and_prevent_duplicate():
    app = make_app()
    with app.app_context():
        db = get_db()
        report = save_weekly_report(db, sample_snapshot())

        assert report["week_start"] == "2026-05-25"
        assert report["adherence_score"] == 82
        with pytest.raises(WeeklyReportExistsError):
            save_weekly_report(db, sample_snapshot())


def test_overwrite_weekly_report():
    app = make_app()
    with app.app_context():
        db = get_db()
        save_weekly_report(db, sample_snapshot(score=70))
        updated = save_weekly_report(
            db,
            sample_snapshot(score=90, recommendation="Snapshot atualizado."),
            overwrite=True,
        )

        assert updated["adherence_score"] == 90
        assert updated["recommendation"] == "Snapshot atualizado."


def test_list_and_delete_weekly_report():
    app = make_app()
    with app.app_context():
        db = get_db()
        report = save_weekly_report(db, sample_snapshot())

        reports = list_weekly_reports(db)
        assert len(reports) == 1

        delete_weekly_report(db, report["id"])
        assert get_weekly_report(db, "2026-05-25") is None
