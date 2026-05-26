import os
import sqlite3
from datetime import date, timedelta

from flask import current_app, g

from app.services.migration_service import apply_pending_migrations


def get_db():
    if current_app.config["DATABASE"] == ":memory:":
        return get_memory_db()

    if "db" not in g:
        database_path = current_app.config["DATABASE"]
        database_dir = os.path.dirname(database_path)
        if database_dir:
            os.makedirs(database_dir, exist_ok=True)
        else:
            os.makedirs(current_app.instance_path, exist_ok=True)
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def get_memory_db():
    db = current_app.extensions.get("memory_db")
    if db is None:
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        current_app.extensions["memory_db"] = db
    return db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    create_schema(db)
    seed_demo_data(db)
    db.commit()


def reset_db():
    db = get_db()
    db.executescript(
        """
        DROP TABLE IF EXISTS weekly_reports;
        DROP TABLE IF EXISTS meal_items;
        DROP TABLE IF EXISTS meals;
        DROP TABLE IF EXISTS measurements;
        DROP TABLE IF EXISTS foods;
        DROP TABLE IF EXISTS profiles;
        DROP TABLE IF EXISTS schema_migrations;
        """
    )
    create_schema(db)
    seed_demo_data(db)
    db.commit()


def create_schema(db):
    apply_pending_migrations(db)
    ensure_weekly_reports_schema(db)


def ensure_weekly_reports_schema(db):
    table_exists = db.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = 'weekly_reports'
        """
    ).fetchone()
    if not table_exists:
        return

    columns = {
        row["name"]
        for row in db.execute("PRAGMA table_info(weekly_reports)").fetchall()
    }
    expected_columns = {
        "updated_at": "TEXT",
        "weight_start": "REAL",
        "weight_end": "REAL",
        "weight_delta": "REAL",
        "avg_calories": "REAL",
        "avg_protein": "REAL",
        "avg_carbs": "REAL",
        "avg_fat": "REAL",
        "waist_delta": "REAL",
        "adherence_score": "REAL",
        "trend_status": "TEXT",
        "weekly_weight_delta": "REAL",
        "moving_average_latest": "REAL",
        "plateau_detected": "INTEGER DEFAULT 0",
        "recommendation": "TEXT",
        "notes": "TEXT",
    }
    for column, definition in expected_columns.items():
        if column not in columns:
            db.execute(f"ALTER TABLE weekly_reports ADD COLUMN {column} {definition}")

    db.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_weekly_reports_week_start
        ON weekly_reports (week_start)
        """
    )


def seed_demo_data(db):
    food_count = db.execute("SELECT COUNT(*) FROM foods").fetchone()[0]
    if food_count == 0:
        db.executemany(
            """
            INSERT INTO foods
                (name, portion_grams, calories, protein_g, carbs_g, fat_g, fiber_g)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("Arroz cozido", 100, 128, 2.5, 28.1, 0.2, 1.6),
                ("Feijao carioca cozido", 100, 76, 4.8, 13.6, 0.5, 8.5),
                ("Peito de frango grelhado", 100, 165, 31.0, 0.0, 3.6, 0.0),
                ("Ovo inteiro", 50, 72, 6.3, 0.4, 4.8, 0.0),
                ("Banana prata", 100, 89, 1.1, 22.8, 0.3, 2.6),
            ],
        )

    measurement_count = db.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]
    if measurement_count == 0:
        today = date.today()
        db.executemany(
            """
            INSERT INTO measurements
                (measurement_date, weight_kg, waist_navel_cm, waist_min_cm, abdomen_cm,
                 chest_cm, hip_cm, right_arm_cm, left_arm_cm, right_thigh_cm,
                 left_thigh_cm, neck_cm, calf_cm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ((today - timedelta(days=14)).isoformat(), 82.0, 91, 84, 94, 102, 99, 34, 34, 58, 58, 39, 38),
                ((today - timedelta(days=7)).isoformat(), 81.2, 89, 83, 93, 102, 99, 34, 34, 58, 58, 39, 38),
                (today.isoformat(), 80.8, 88, 82, 92, 102, 98, 34, 34, 57, 57, 39, 38),
            ],
        )


def seed_example_data(db):
    seed_demo_data(db)
