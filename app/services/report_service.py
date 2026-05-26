class WeeklyReportExistsError(Exception):
    pass


REPORT_FIELDS = [
    "week_start",
    "week_end",
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
    "score",
    "summary",
]


def build_weekly_report_snapshot(start, end, summary, trend_analysis, notes=""):
    return {
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "weight_start": summary["weight_start"],
        "weight_end": summary["weight_end"],
        "weight_delta": summary["weight_delta"],
        "avg_calories": summary["avg_calories"],
        "avg_protein": summary["avg_protein_g"],
        "avg_carbs": summary["avg_carbs_g"],
        "avg_fat": summary["avg_fat_g"],
        "waist_delta": summary["waist_delta"],
        "adherence_score": summary["adherence"]["score"],
        "trend_status": trend_analysis["trend"]["classification"],
        "weekly_weight_delta": trend_analysis["weekly_delta"],
        "moving_average_latest": trend_analysis["latest_moving_average"],
        "plateau_detected": 1 if trend_analysis["plateau"]["plateau_detected"] else 0,
        "recommendation": trend_analysis["recommendation"],
        "notes": notes,
        "score": summary["adherence"]["score"],
        "summary": trend_analysis["recommendation"],
    }


def save_weekly_report(db, snapshot, overwrite=False):
    existing = get_weekly_report(db, snapshot["week_start"])
    if existing and not overwrite:
        raise WeeklyReportExistsError("Ja existe relatorio salvo para esta semana.")

    if existing:
        assignments = ", ".join([f"{field} = ?" for field in REPORT_FIELDS if field != "week_start"])
        values = [snapshot[field] for field in REPORT_FIELDS if field != "week_start"]
        values.append(snapshot["week_start"])
        db.execute(
            f"""
            UPDATE weekly_reports
            SET {assignments}, updated_at = CURRENT_TIMESTAMP
            WHERE week_start = ?
            """,
            values,
        )
    else:
        placeholders = ", ".join(["?"] * len(REPORT_FIELDS))
        columns = ", ".join(REPORT_FIELDS)
        db.execute(
            f"""
            INSERT INTO weekly_reports ({columns})
            VALUES ({placeholders})
            """,
            [snapshot[field] for field in REPORT_FIELDS],
        )
    db.commit()
    return get_weekly_report(db, snapshot["week_start"])


def get_weekly_report(db, week_start):
    return db.execute(
        "SELECT * FROM weekly_reports WHERE week_start = ?",
        (week_start,),
    ).fetchone()


def get_weekly_report_by_id(db, report_id):
    return db.execute(
        "SELECT * FROM weekly_reports WHERE id = ?",
        (report_id,),
    ).fetchone()


def list_weekly_reports(db, limit=None):
    sql = "SELECT * FROM weekly_reports ORDER BY week_start DESC"
    params = ()
    if limit:
        sql += " LIMIT ?"
        params = (limit,)
    return db.execute(sql, params).fetchall()


def delete_weekly_report(db, report_id):
    db.execute("DELETE FROM weekly_reports WHERE id = ?", (report_id,))
    db.commit()


def serialize_weekly_report(report):
    if report is None:
        return None
    return {key: report[key] for key in report.keys()}
