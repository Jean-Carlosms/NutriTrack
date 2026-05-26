import pytest

from app.services.bodyfat_service import (
    calculate_bmi,
    calculate_us_navy_bodyfat,
    calculate_waist_height_ratio,
)


def test_calculate_bmi():
    assert calculate_bmi(weight_kg=80, height_cm=180) == 24.69


def test_calculate_waist_height_ratio():
    assert calculate_waist_height_ratio(waist_cm=90, height_cm=180) == 0.5


def test_calculate_us_navy_bodyfat_male():
    result = calculate_us_navy_bodyfat(
        sex="male",
        height_cm=180,
        neck_cm=39,
        waist_cm=90,
    )

    assert result == 19.2


def test_calculate_us_navy_bodyfat_female():
    result = calculate_us_navy_bodyfat(
        sex="female",
        height_cm=165,
        neck_cm=34,
        waist_cm=76,
        hip_cm=98,
    )

    assert result == 28.73


def test_bodyfat_calculations_reject_invalid_values():
    with pytest.raises(ValueError):
        calculate_bmi(weight_kg=0, height_cm=180)
    with pytest.raises(ValueError):
        calculate_bmi(weight_kg=80, height_cm=0)
    with pytest.raises(ValueError):
        calculate_waist_height_ratio(waist_cm=0, height_cm=180)
    with pytest.raises(ValueError):
        calculate_waist_height_ratio(waist_cm=90, height_cm=0)


def test_us_navy_bodyfat_rejects_missing_or_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_us_navy_bodyfat(sex="", height_cm=180, neck_cm=39, waist_cm=90)
    with pytest.raises(ValueError):
        calculate_us_navy_bodyfat(sex="female", height_cm=165, neck_cm=34, waist_cm=76)
    with pytest.raises(ValueError):
        calculate_us_navy_bodyfat(sex="male", height_cm=180, neck_cm=90, waist_cm=90)
