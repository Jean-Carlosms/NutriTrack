import pytest

from app.services.macro_service import calculate_food_amount, calculate_macro_targets


def test_calculate_macro_targets_for_fat_loss():
    targets = calculate_macro_targets(weight_kg=80, calories=2000, goal="fat_loss")

    assert targets["protein_g"] == 160
    assert targets["fat_g"] == 48
    assert targets["carbs_g"] == 232
    assert targets["protein_per_kg"] == 2.0


def test_calculate_food_amount_proportionally():
    food = {
        "portion_grams": 100,
        "calories": 200,
        "protein_g": 20,
        "carbs_g": 10,
        "fat_g": 8,
        "fiber_g": 2,
    }

    amount = calculate_food_amount(food, 50)

    assert amount == {
        "calories": 100,
        "protein_g": 10,
        "carbs_g": 5,
        "fat_g": 4,
        "fiber_g": 1,
    }


def test_calculate_macro_targets_rejects_invalid_values():
    with pytest.raises(ValueError):
        calculate_macro_targets(weight_kg=0, calories=2000, goal="fat_loss")
    with pytest.raises(ValueError):
        calculate_macro_targets(weight_kg=80, calories=0, goal="fat_loss")
    with pytest.raises(ValueError):
        calculate_macro_targets(weight_kg=80, calories=2000, goal="unknown")


def test_calculate_food_amount_rejects_invalid_values():
    food = {
        "portion_grams": 0,
        "calories": 200,
        "protein_g": 20,
        "carbs_g": 10,
        "fat_g": 8,
        "fiber_g": 2,
    }
    with pytest.raises(ValueError):
        calculate_food_amount(food, 50)

    food["portion_grams"] = 100
    with pytest.raises(ValueError):
        calculate_food_amount(food, 0)
