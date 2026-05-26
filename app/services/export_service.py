import csv
import io


FOOD_HEADERS = [
    "id",
    "nome",
    "porcao_gramas",
    "calorias",
    "proteina_g",
    "carboidratos_g",
    "gorduras_g",
    "fibras_g",
]

MEAL_HEADERS = ["id", "data", "tipo_refeicao"]

MEAL_ITEM_HEADERS = [
    "id",
    "data",
    "tipo_refeicao",
    "alimento",
    "quantidade_gramas",
    "calorias",
    "proteina_g",
    "carboidratos_g",
    "gorduras_g",
    "fibras_g",
]

MEASUREMENT_HEADERS = [
    "id",
    "data",
    "peso_kg",
    "cintura_umbigo_cm",
    "cintura_fina_cm",
    "abdomen_cm",
    "peito_cm",
    "quadril_cm",
    "braco_direito_cm",
    "braco_esquerdo_cm",
    "coxa_direita_cm",
    "coxa_esquerda_cm",
    "pescoco_cm",
    "panturrilha_cm",
]

WEEKLY_REPORT_HEADERS = [
    "semana_inicio",
    "semana_fim",
    "peso_inicial_kg",
    "peso_final_kg",
    "variacao_peso_kg",
    "media_calorias",
    "media_proteina_g",
    "media_carboidratos_g",
    "media_gorduras_g",
    "variacao_cintura_cm",
    "score_aderencia",
    "classificacao",
    "observacao",
]

WEEKLY_REPORT_HISTORY_HEADERS = [
    "week_start",
    "week_end",
    "created_at",
    "updated_at",
    "weight_start",
    "weight_end",
    "weight_delta",
    "avg_calories",
    "avg_protein",
    "avg_carbs",
    "avg_fat",
    "waist_delta",
    "adherence_score",
    "trend_status",
    "weekly_weight_delta",
    "moving_average_latest",
    "plateau_detected",
    "recommendation",
    "notes",
]


def rows_to_csv(headers, rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


def export_foods(rows):
    return rows_to_csv(
        FOOD_HEADERS,
        [
            [
                row["id"],
                row["name"],
                row["portion_grams"],
                row["calories"],
                row["protein_g"],
                row["carbs_g"],
                row["fat_g"],
                row["fiber_g"] or 0,
            ]
            for row in rows
        ],
    )


def export_meals(rows):
    return rows_to_csv(
        MEAL_HEADERS,
        [[row["id"], row["meal_date"], row["meal_type"]] for row in rows],
    )


def export_meal_items(rows):
    return rows_to_csv(
        MEAL_ITEM_HEADERS,
        [
            [
                row["id"],
                row["meal_date"],
                row["meal_type"],
                row["food_name"],
                row["quantity_grams"],
                row["calories"],
                row["protein_g"],
                row["carbs_g"],
                row["fat_g"],
                row["fiber_g"],
            ]
            for row in rows
        ],
    )


def export_measurements(rows):
    return rows_to_csv(
        MEASUREMENT_HEADERS,
        [
            [
                row["id"],
                row["measurement_date"],
                row["weight_kg"],
                row["waist_navel_cm"],
                row["waist_min_cm"],
                row["abdomen_cm"],
                row["chest_cm"],
                row["hip_cm"],
                row["right_arm_cm"],
                row["left_arm_cm"],
                row["right_thigh_cm"],
                row["left_thigh_cm"],
                row["neck_cm"],
                row["calf_cm"],
            ]
            for row in rows
        ],
    )


def export_weekly_report(start, end, summary):
    row = [
        start.isoformat(),
        end.isoformat(),
        summary["weight_start"],
        summary["weight_end"],
        summary["weight_delta"],
        summary["avg_calories"],
        summary["avg_protein_g"],
        summary["avg_carbs_g"],
        summary["avg_fat_g"],
        summary["waist_delta"],
        summary["adherence"]["score"],
        summary["adherence"]["classification"],
        summary["observation"],
    ]
    return rows_to_csv(WEEKLY_REPORT_HEADERS, [row])


def export_weekly_reports_history(rows):
    return rows_to_csv(
        WEEKLY_REPORT_HISTORY_HEADERS,
        [
            [
                row["week_start"],
                row["week_end"],
                row["created_at"],
                row["updated_at"],
                row["weight_start"],
                row["weight_end"],
                row["weight_delta"],
                row["avg_calories"],
                row["avg_protein"],
                row["avg_carbs"],
                row["avg_fat"],
                row["waist_delta"],
                row["adherence_score"],
                row["trend_status"],
                row["weekly_weight_delta"],
                row["moving_average_latest"],
                row["plateau_detected"],
                row["recommendation"],
                row["notes"],
            ]
            for row in rows
        ],
    )
