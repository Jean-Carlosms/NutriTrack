ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "athlete": 1.9,
}

GOAL_ADJUSTMENTS = {
    "fat_loss": -500,
    "maintenance": 0,
    "muscle_gain": 300,
    "recomposition": -150,
}


def calculate_bmr(weight_kg, height_cm, age, sex):
    if weight_kg <= 0:
        raise ValueError("peso deve ser maior que zero")
    if height_cm <= 0:
        raise ValueError("altura deve ser maior que zero")
    if age <= 0:
        raise ValueError("idade deve ser maior que zero")

    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    normalized_sex = str(sex).lower()
    if normalized_sex in {"male", "m", "masculino"}:
        return round(base + 5, 2)
    if normalized_sex in {"female", "f", "feminino"}:
        return round(base - 161, 2)
    raise ValueError("sexo deve ser 'male' ou 'female'")


def calculate_tdee(bmr, activity_level):
    if bmr <= 0:
        raise ValueError("TMB deve ser maior que zero")

    factor = ACTIVITY_FACTORS.get(activity_level)
    if factor is None:
        raise ValueError("nivel de atividade invalido")
    return round(bmr * factor, 2)


def calculate_daily_calorie_target(tdee, goal):
    if tdee <= 0:
        raise ValueError("GETD deve ser maior que zero")

    adjustment = GOAL_ADJUSTMENTS.get(goal)
    if adjustment is None:
        raise ValueError("objetivo invalido")
    return round(max(tdee + adjustment, 1200), 2)


def calculate_calorie_plan(profile):
    bmr = calculate_bmr(
        weight_kg=profile["current_weight_kg"],
        height_cm=profile["height_cm"],
        age=profile["age"],
        sex=profile["sex"],
    )
    tdee = calculate_tdee(bmr, profile["activity_level"])
    target = calculate_daily_calorie_target(tdee, profile["goal"])
    return {"bmr": bmr, "tdee": tdee, "target_calories": target}
