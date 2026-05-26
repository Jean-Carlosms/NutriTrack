from app.services.adherence_service import calculate_weekly_adherence


def build_weekly_summary(daily_totals, measurements, calorie_target, macro_targets, goal):
    if calorie_target <= 0:
        raise ValueError("meta calorica deve ser maior que zero")
    if macro_targets["protein_g"] <= 0:
        raise ValueError("meta de proteina deve ser maior que zero")

    sorted_measurements = sorted(measurements, key=lambda item: item["measurement_date"])
    weight_start = sorted_measurements[0]["weight_kg"] if sorted_measurements else None
    weight_end = sorted_measurements[-1]["weight_kg"] if sorted_measurements else None

    waist_start = sorted_measurements[0]["waist_navel_cm"] if sorted_measurements else None
    waist_end = sorted_measurements[-1]["waist_navel_cm"] if sorted_measurements else None

    calories = [day.get("calories", 0) for day in daily_totals]
    protein = [day.get("protein_g", 0) for day in daily_totals]
    carbs = [day.get("carbs_g", 0) for day in daily_totals]
    fat = [day.get("fat_g", 0) for day in daily_totals]

    adherence = calculate_weekly_adherence(
        daily_totals=daily_totals,
        target_calories=calorie_target,
        protein_target_g=macro_targets["protein_g"],
        weight_start=weight_start,
        weight_end=weight_end,
        goal=goal,
    )

    observation = make_observation(
        adherence["score"],
        average(protein),
        macro_targets["protein_g"],
        average(calories),
        calorie_target,
        weight_start,
        weight_end,
    )

    return {
        "weight_start": weight_start,
        "weight_end": weight_end,
        "weight_delta": round(weight_end - weight_start, 2)
        if weight_start is not None and weight_end is not None
        else None,
        "avg_calories": round(average(calories), 1),
        "avg_protein_g": round(average(protein), 1),
        "avg_carbs_g": round(average(carbs), 1),
        "avg_fat_g": round(average(fat), 1),
        "waist_delta": round(waist_end - waist_start, 2)
        if waist_start is not None and waist_end is not None
        else None,
        "adherence": adherence,
        "observation": observation,
    }


def average(values):
    return sum(values) / len(values) if values else 0


def make_observation(
    score,
    avg_protein,
    protein_target,
    avg_calories,
    calorie_target,
    weight_start=None,
    weight_end=None,
):
    if avg_calories < calorie_target * 0.75:
        return "Calorias muito abaixo da meta. Risco de baixa sustentabilidade."
    if avg_protein < protein_target * 0.8:
        return "Proteina media abaixo da meta. Considere aumentar fontes proteicas nas refeicoes."
    if score >= 75:
        return "Boa aderencia semanal. Manter estrategia atual."
    if weight_start is not None and weight_end is not None and abs(weight_end - weight_start) < 0.2:
        return "Peso estavel com baixa aderencia. Melhorar a consistencia dos registros pode ajudar a leitura da evolucao."
    return "Aderencia semanal irregular. Revisar registros e metas."
