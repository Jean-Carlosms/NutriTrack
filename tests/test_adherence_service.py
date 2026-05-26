import pytest

from app.services.adherence_service import (
    calculate_weekly_adherence,
    classify_score,
)


def test_classify_score():
    assert classify_score(95) == "excelente"
    assert classify_score(80) == "boa"
    assert classify_score(65) == "regular"
    assert classify_score(50) == "baixa"


def test_calculate_weekly_adherence_good_week():
    daily_totals = [
        {"calories": 2000, "protein_g": 160},
        {"calories": 1950, "protein_g": 150},
        {"calories": 2050, "protein_g": 165},
        {"calories": 2000, "protein_g": 160},
        {"calories": 1900, "protein_g": 145},
        {"calories": 2100, "protein_g": 170},
        {"calories": 1980, "protein_g": 155},
    ]

    result = calculate_weekly_adherence(
        daily_totals=daily_totals,
        target_calories=2000,
        protein_target_g=160,
        weight_start=80,
        weight_end=79.5,
        goal="fat_loss",
    )

    assert result["score"] >= 90
    assert result["classification"] == "excelente"


def test_calculate_weekly_adherence_penalizes_missing_logs():
    daily_totals = [
        {"calories": 2000, "protein_g": 160},
        {"calories": 0, "protein_g": 0},
        {"calories": 0, "protein_g": 0},
    ]

    result = calculate_weekly_adherence(
        daily_totals=daily_totals,
        target_calories=2000,
        protein_target_g=160,
        goal="maintenance",
    )

    assert result["components"]["consistency"] < 10


def test_calculate_weekly_adherence_handles_absence_of_meals():
    result = calculate_weekly_adherence(
        daily_totals=[],
        target_calories=2000,
        protein_target_g=160,
        goal="maintenance",
    )

    assert result["score"] == 5
    assert result["classification"] == "baixa"


def test_calculate_weekly_adherence_rejects_invalid_targets_and_goal():
    with pytest.raises(ValueError):
        calculate_weekly_adherence([], target_calories=0, protein_target_g=160)
    with pytest.raises(ValueError):
        calculate_weekly_adherence([], target_calories=2000, protein_target_g=0)
    with pytest.raises(ValueError):
        calculate_weekly_adherence([], target_calories=2000, protein_target_g=160, goal="unknown")
