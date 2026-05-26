from datetime import date


TREND_REDUCING = "reduzindo"
TREND_INCREASING = "aumentando"
TREND_STABLE = "estavel"
TREND_INSUFFICIENT = "dados insuficientes"


def calculate_moving_average(measurements, window=7):
    ordered = normalize_measurements(measurements)
    if not ordered:
        return []
    if window <= 0:
        raise ValueError("janela deve ser maior que zero")

    result = []
    for index, measurement in enumerate(ordered):
        start = max(0, index - window + 1)
        values = [item["weight_kg"] for item in ordered[start : index + 1]]
        result.append(
            {
                "measurement_date": measurement["measurement_date"],
                "weight_kg": measurement["weight_kg"],
                "moving_average": round(sum(values) / len(values), 2),
            }
        )
    return result


def calculate_weight_trend(measurements):
    ordered = normalize_measurements(measurements)
    if len(ordered) < 2:
        return {
            "status": "insufficient_data",
            "classification": TREND_INSUFFICIENT,
            "weight_delta": None,
            "period_days": 0,
            "weekly_delta": None,
            "explanation": "Registre pelo menos duas medidas para calcular tendencia.",
        }

    first = ordered[0]
    last = ordered[-1]
    period_days = max((last["date"] - first["date"]).days, 0)
    weight_delta = round(last["weight_kg"] - first["weight_kg"], 2)
    weekly_delta = round(weight_delta / period_days * 7, 2) if period_days else weight_delta

    if abs(weight_delta) <= 0.3:
        classification = TREND_STABLE
    elif weight_delta < 0:
        classification = TREND_REDUCING
    else:
        classification = TREND_INCREASING

    return {
        "status": "ok",
        "classification": classification,
        "weight_delta": weight_delta,
        "period_days": period_days,
        "weekly_delta": weekly_delta,
        "explanation": build_trend_explanation(classification, weight_delta, period_days),
    }


def calculate_weekly_weight_delta(measurements):
    trend = calculate_weight_trend(measurements)
    if trend["status"] != "ok":
        return None
    return trend["weekly_delta"]


def detect_plateau(measurements, days=14, threshold_kg=0.3):
    ordered = normalize_measurements(measurements)
    if len(ordered) < 2:
        return insufficient_plateau(days)

    latest = ordered[-1]
    period_start_date = latest["date"] - date_delta(days)
    window = [item for item in ordered if item["date"] >= period_start_date]
    if len(window) < 2:
        return insufficient_plateau(days)

    period_days = (window[-1]["date"] - window[0]["date"]).days
    if period_days < days:
        return insufficient_plateau(days, period_days=period_days)

    weight_delta = round(window[-1]["weight_kg"] - window[0]["weight_kg"], 2)
    plateau_detected = abs(weight_delta) <= threshold_kg
    explanation = (
        f"Peso variou {weight_delta} kg em {period_days} dias, dentro do limite de {threshold_kg} kg."
        if plateau_detected
        else f"Peso variou {weight_delta} kg em {period_days} dias, acima do limite de {threshold_kg} kg."
    )
    return {
        "status": "ok",
        "plateau_detected": plateau_detected,
        "period_days": period_days,
        "weight_delta": weight_delta,
        "explanation": explanation,
    }


def analyze_calorie_adherence_vs_weight(meals_summary, measurements):
    trend = calculate_weight_trend(measurements)
    average_calories = meals_summary.get("avg_calories", 0) if meals_summary else 0
    target_calories = meals_summary.get("target_calories", 0) if meals_summary else 0
    adherence_score = meals_summary.get("adherence_score", 0) if meals_summary else 0

    calorie_ratio = average_calories / target_calories if target_calories else None
    if trend["status"] != "ok" or calorie_ratio is None:
        status = "insufficient_data"
    elif calorie_ratio < 0.75:
        status = "calories_too_low"
    elif trend["classification"] == TREND_REDUCING and 0.85 <= calorie_ratio <= 1.15:
        status = "aligned"
    elif trend["classification"] == TREND_STABLE and adherence_score < 60:
        status = "low_adherence_stable_weight"
    elif trend["classification"] == TREND_STABLE and adherence_score >= 75:
        status = "high_adherence_stable_weight"
    else:
        status = "monitor"

    return {
        "status": status,
        "trend": trend,
        "average_calories": round(average_calories, 1),
        "target_calories": round(target_calories, 1) if target_calories else None,
        "calorie_ratio": round(calorie_ratio, 2) if calorie_ratio is not None else None,
        "adherence_score": adherence_score,
    }


def generate_trend_recommendation(trend_data):
    status = trend_data.get("status")
    trend = trend_data.get("trend", {})
    if status == "insufficient_data":
        return "Registre mais dias de refeicoes e medidas para uma leitura mais confiavel."
    if status == "calories_too_low":
        return "Calorias medias muito abaixo da meta. Isso pode reduzir a sustentabilidade; revise a estrategia com cuidado."
    if status == "aligned":
        return "Aderencia calorica proxima da meta e peso reduzindo. Manter a estrategia atual pode ser adequado."
    if status == "low_adherence_stable_weight":
        return "Peso estavel com baixa aderencia. Priorize consistencia dos registros antes de ajustar metas."
    if status == "high_adherence_stable_weight":
        return "Peso estavel com boa aderencia por periodo relevante. Considere reavaliar a meta calorica com um profissional."
    if trend.get("classification") == TREND_INCREASING:
        return "Peso em aumento no periodo. Observe contexto, registros e objetivo antes de fazer ajustes."
    return "Continue registrando medidas e refeicoes para acompanhar a tendencia com mais clareza."


def build_trend_analysis(measurements, meals_summary=None, moving_average_window=7):
    moving_average = calculate_moving_average(measurements, window=moving_average_window)
    trend = calculate_weight_trend(measurements)
    plateau = detect_plateau(measurements)
    adherence_vs_weight = analyze_calorie_adherence_vs_weight(meals_summary or {}, measurements)
    recommendation = generate_trend_recommendation(adherence_vs_weight)
    latest_moving_average = moving_average[-1]["moving_average"] if moving_average else None

    return {
        "moving_average": moving_average,
        "latest_moving_average": latest_moving_average,
        "trend": trend,
        "weekly_delta": calculate_weekly_weight_delta(measurements),
        "plateau": plateau,
        "adherence_vs_weight": adherence_vs_weight,
        "recommendation": recommendation,
    }


def normalize_measurements(measurements):
    normalized = []
    for measurement in measurements:
        measurement_date = measurement["measurement_date"]
        parsed_date = date.fromisoformat(measurement_date)
        weight = measurement["weight_kg"]
        if weight is None:
            continue
        normalized.append(
            {
                "measurement_date": measurement_date,
                "date": parsed_date,
                "weight_kg": float(weight),
            }
        )
    return sorted(normalized, key=lambda item: item["date"])


def build_trend_explanation(classification, weight_delta, period_days):
    if classification == TREND_REDUCING:
        return f"Peso reduziu {abs(weight_delta)} kg em {period_days} dias."
    if classification == TREND_INCREASING:
        return f"Peso aumentou {weight_delta} kg em {period_days} dias."
    return f"Peso ficou estavel no periodo, com variacao de {weight_delta} kg."


def insufficient_plateau(days, period_days=0):
    return {
        "status": "insufficient_data",
        "plateau_detected": False,
        "period_days": period_days,
        "weight_delta": None,
        "explanation": f"Sao necessarios pelo menos {days} dias de medidas para avaliar plato.",
    }


def date_delta(days):
    from datetime import timedelta

    return timedelta(days=days)
