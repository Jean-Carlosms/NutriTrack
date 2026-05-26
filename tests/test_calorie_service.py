import pytest

from app.services.calorie_service import (
    calculate_bmr,
    calculate_daily_calorie_target,
    calculate_tdee,
)


def test_calculate_bmr_mifflin_male():
    assert calculate_bmr(weight_kg=80, height_cm=180, age=30, sex="male") == 1780


def test_calculate_bmr_mifflin_female():
    assert calculate_bmr(weight_kg=65, height_cm=165, age=28, sex="female") == 1380.25


def test_calculate_tdee_from_activity_factor():
    assert calculate_tdee(1780, "moderate") == 2759


def test_calculate_daily_calorie_target_by_goal():
    assert calculate_daily_calorie_target(2500, "fat_loss") == 2000
    assert calculate_daily_calorie_target(2500, "muscle_gain") == 2800


def test_invalid_activity_level_raises_error():
    with pytest.raises(ValueError):
        calculate_tdee(1800, "invalid")


def test_calculate_bmr_rejects_zero_or_negative_values():
    with pytest.raises(ValueError):
        calculate_bmr(weight_kg=0, height_cm=180, age=30, sex="male")
    with pytest.raises(ValueError):
        calculate_bmr(weight_kg=80, height_cm=0, age=30, sex="male")
    with pytest.raises(ValueError):
        calculate_bmr(weight_kg=80, height_cm=180, age=-1, sex="male")


def test_calculate_bmr_rejects_invalid_sex():
    with pytest.raises(ValueError):
        calculate_bmr(weight_kg=80, height_cm=180, age=30, sex="")


def test_calorie_target_rejects_zero_tdee_and_unknown_goal():
    with pytest.raises(ValueError):
        calculate_daily_calorie_target(0, "fat_loss")
    with pytest.raises(ValueError):
        calculate_daily_calorie_target(2500, "unknown")
