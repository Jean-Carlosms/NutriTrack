def classify_score(score):
    if score >= 90:
        return "excelente"
    if score >= 75:
        return "boa"
    if score >= 60:
        return "regular"
    return "baixa"


def _average(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else 0


def calculate_weekly_adherence(
    daily_totals,
    target_calories,
    protein_target_g,
    weight_start=None,
    weight_end=None,
    goal="maintenance",
):
    if target_calories <= 0:
        raise ValueError("meta calorica deve ser maior que zero")
    if protein_target_g <= 0:
        raise ValueError("meta de proteina deve ser maior que zero")
    if goal not in {"fat_loss", "maintenance", "muscle_gain", "recomposition"}:
        raise ValueError("objetivo invalido")

    logged_days = [day for day in daily_totals if day.get("calories", 0) > 0]
    consistency_score = min(len(logged_days) / 7, 1) * 20

    calorie_scores = []
    protein_scores = []
    for day in logged_days:
        calorie_delta = abs(day.get("calories", 0) - target_calories)
        calorie_scores.append(max(0, 1 - calorie_delta / (target_calories * 0.25)))
        protein_scores.append(min(day.get("protein_g", 0) / protein_target_g, 1))

    calorie_score = _average(calorie_scores) * 40
    protein_score = _average(protein_scores) * 30
    progress_score = calculate_weight_progress_score(weight_start, weight_end, goal)

    score = round(calorie_score + protein_score + consistency_score + progress_score, 1)
    return {
        "score": min(score, 100),
        "classification": classify_score(score),
        "components": {
            "calories": round(calorie_score, 1),
            "protein": round(protein_score, 1),
            "consistency": round(consistency_score, 1),
            "progress": round(progress_score, 1),
        },
    }


def calculate_weight_progress_score(weight_start, weight_end, goal):
    if goal not in {"fat_loss", "maintenance", "muscle_gain", "recomposition"}:
        raise ValueError("objetivo invalido")

    if weight_start is None or weight_end is None:
        return 5

    delta = weight_end - weight_start
    if goal == "fat_loss":
        return 10 if delta <= 0 else max(0, 10 - delta * 10)
    if goal == "muscle_gain":
        return 10 if delta >= 0 else max(0, 10 + delta * 10)
    if goal == "recomposition":
        return 10 if abs(delta) <= 0.5 else 6
    return 10 if abs(delta) <= 0.5 else 7
