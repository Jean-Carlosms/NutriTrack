from app.services.trend_service import (
    analyze_calorie_adherence_vs_weight,
    build_trend_analysis,
    calculate_moving_average,
    calculate_weight_trend,
    detect_plateau,
    generate_trend_recommendation,
)


def measurement(day, weight):
    return {"measurement_date": day, "weight_kg": weight}


def test_weight_trend_without_measurements():
    trend = calculate_weight_trend([])

    assert trend["status"] == "insufficient_data"
    assert trend["classification"] == "dados insuficientes"


def test_weight_trend_with_one_measurement():
    trend = calculate_weight_trend([measurement("2026-05-01", 80)])

    assert trend["status"] == "insufficient_data"


def test_weight_trend_reducing():
    trend = calculate_weight_trend([
        measurement("2026-05-01", 80),
        measurement("2026-05-08", 79),
    ])

    assert trend["classification"] == "reduzindo"
    assert trend["weight_delta"] == -1


def test_weight_trend_increasing():
    trend = calculate_weight_trend([
        measurement("2026-05-01", 80),
        measurement("2026-05-08", 81),
    ])

    assert trend["classification"] == "aumentando"


def test_weight_trend_stable():
    trend = calculate_weight_trend([
        measurement("2026-05-01", 80),
        measurement("2026-05-08", 80.2),
    ])

    assert trend["classification"] == "estavel"


def test_calculate_moving_average():
    result = calculate_moving_average(
        [
            measurement("2026-05-01", 80),
            measurement("2026-05-02", 79),
            measurement("2026-05-03", 78),
        ],
        window=2,
    )

    assert result[-1]["moving_average"] == 78.5


def test_plateau_detected():
    plateau = detect_plateau(
        [
            measurement("2026-05-01", 80),
            measurement("2026-05-15", 80.2),
        ],
        days=14,
        threshold_kg=0.3,
    )

    assert plateau["status"] == "ok"
    assert plateau["plateau_detected"] is True


def test_plateau_not_detected():
    plateau = detect_plateau(
        [
            measurement("2026-05-01", 80),
            measurement("2026-05-15", 79),
        ],
        days=14,
        threshold_kg=0.3,
    )

    assert plateau["plateau_detected"] is False


def test_plateau_insufficient_data():
    plateau = detect_plateau([measurement("2026-05-01", 80)], days=14)

    assert plateau["status"] == "insufficient_data"


def test_recommendation_with_insufficient_data():
    analysis = analyze_calorie_adherence_vs_weight({}, [])

    assert generate_trend_recommendation(analysis).startswith("Registre mais dias")


def test_recommendation_for_low_adherence_stable_weight():
    analysis = analyze_calorie_adherence_vs_weight(
        {"avg_calories": 1900, "target_calories": 2000, "adherence_score": 40},
        [
            measurement("2026-05-01", 80),
            measurement("2026-05-15", 80.1),
        ],
    )

    assert analysis["status"] == "low_adherence_stable_weight"
    assert "consistencia" in generate_trend_recommendation(analysis)


def test_recommendation_for_high_adherence_stable_weight():
    analysis = analyze_calorie_adherence_vs_weight(
        {"avg_calories": 1980, "target_calories": 2000, "adherence_score": 85},
        [
            measurement("2026-05-01", 80),
            measurement("2026-05-15", 80.1),
        ],
    )

    assert analysis["status"] == "high_adherence_stable_weight"
    assert "reavaliar" in generate_trend_recommendation(analysis)


def test_build_trend_analysis_returns_safe_structure():
    analysis = build_trend_analysis([measurement("2026-05-01", 80)])

    assert analysis["latest_moving_average"] == 80
    assert analysis["trend"]["status"] == "insufficient_data"
