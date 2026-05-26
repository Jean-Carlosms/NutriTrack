PROTEIN_BY_GOAL = {
    "fat_loss": 2.0,
    "maintenance": 1.6,
    "muscle_gain": 1.8,
    "recomposition": 2.0,
}


def calculate_macro_targets(weight_kg, calories, goal):
    if weight_kg <= 0:
        raise ValueError("peso deve ser maior que zero")
    if calories <= 0:
        raise ValueError("calorias devem ser maiores que zero")

    protein_per_kg = PROTEIN_BY_GOAL.get(goal)
    if protein_per_kg is None:
        raise ValueError("objetivo invalido")

    protein_g = round(weight_kg * protein_per_kg, 1)
    fat_g = round(max(weight_kg * 0.6, calories * 0.2 / 9), 1)

    protein_calories = protein_g * 4
    fat_calories = fat_g * 9
    carbs_calories = max(calories - protein_calories - fat_calories, 0)
    carbs_g = round(carbs_calories / 4, 1)

    return {
        "protein_g": protein_g,
        "fat_g": fat_g,
        "carbs_g": carbs_g,
        "protein_per_kg": protein_per_kg,
    }


def calculate_food_amount(food, quantity_grams):
    if food["portion_grams"] <= 0:
        raise ValueError("porcao do alimento deve ser maior que zero")
    if quantity_grams <= 0:
        raise ValueError("quantidade consumida deve ser maior que zero")

    ratio = quantity_grams / food["portion_grams"]
    return {
        "calories": round(food["calories"] * ratio, 2),
        "protein_g": round(food["protein_g"] * ratio, 2),
        "carbs_g": round(food["carbs_g"] * ratio, 2),
        "fat_g": round(food["fat_g"] * ratio, 2),
        "fiber_g": round((food["fiber_g"] or 0) * ratio, 2),
    }
