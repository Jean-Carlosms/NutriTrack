import pytest

from app.services.progress_service import build_weekly_summary


def test_build_weekly_summary_without_measurements_or_meals():
    summary = build_weekly_summary(
        daily_totals=[],
        measurements=[],
        calorie_target=2000,
        macro_targets={"protein_g": 160},
        goal="maintenance",
    )

    assert summary["weight_start"] is None
    assert summary["weight_end"] is None
    assert summary["avg_calories"] == 0
    assert summary["avg_protein_g"] == 0
    assert summary["adherence"]["classification"] == "baixa"


def test_build_weekly_summary_rejects_invalid_targets():
    with pytest.raises(ValueError):
        build_weekly_summary([], [], 0, {"protein_g": 160}, "maintenance")
    with pytest.raises(ValueError):
        build_weekly_summary([], [], 2000, {"protein_g": 0}, "maintenance")
