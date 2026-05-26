import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

from app.database import get_db, init_db
from app.services.migration_service import (
    MigrationError,
    apply_migration,
    apply_pending_migrations,
    ensure_migration_table,
    get_applied_migrations,
    get_migration_status,
    get_pending_migrations,
    list_migration_files,
)
from tests.test_app import make_app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ARTIFACTS = PROJECT_ROOT / "test-artifacts"


def memory_db():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    return db


def make_artifact_dir(name):
    path = TEST_ARTIFACTS / f"{name}-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_schema_migrations_table_is_created():
    db = memory_db()

    ensure_migration_table(db)
    table = db.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = 'schema_migrations'
        """
    ).fetchone()

    assert table is not None


def test_migration_files_are_listed_in_order():
    migrations = list_migration_files()
    versions = [migration.version for migration in migrations]

    assert versions == sorted(versions)
    assert versions[:3] == ["001", "002", "003"]


def test_pending_migrations_are_detected_and_registered():
    db = memory_db()

    pending = get_pending_migrations(db)
    applied = apply_pending_migrations(db)
    applied_versions = [migration["version"] for migration in get_applied_migrations(db)]

    assert len(pending) >= 3
    assert [migration.version for migration in applied] == applied_versions
    assert get_pending_migrations(db) == []


def test_applied_migration_does_not_run_again():
    db = memory_db()
    migrations_dir = make_artifact_dir("migrations-once")
    try:
        migration = migrations_dir / "001_insert_sample.sql"
        migration.write_text(
            """
            CREATE TABLE IF NOT EXISTS sample_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
            INSERT INTO sample_items (name) VALUES ('demo');
            """,
            encoding="utf-8",
        )

        first_run = apply_pending_migrations(db, migrations_dir)
        second_run = apply_pending_migrations(db, migrations_dir)
        count = db.execute("SELECT COUNT(*) FROM sample_items").fetchone()[0]

        assert len(first_run) == 1
        assert second_run == []
        assert count == 1
    finally:
        shutil.rmtree(migrations_dir, ignore_errors=True)


def test_failed_migration_raises_clear_error_and_is_not_registered():
    db = memory_db()
    migrations_dir = make_artifact_dir("migrations-failure")
    try:
        bad_migration = migrations_dir / "001_bad_sql.sql"
        bad_migration.write_text("CREATE TABLE broken (id INTEGER;", encoding="utf-8")

        with pytest.raises(MigrationError):
            apply_pending_migrations(db, migrations_dir)

        assert get_applied_migrations(db) == []
    finally:
        shutil.rmtree(migrations_dir, ignore_errors=True)


def test_new_database_receives_all_migrations_through_init_db():
    app = make_app()
    with app.app_context():
        db = get_db()
        tables = {
            row["name"]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        status = get_migration_status(db)

    assert "profiles" in tables
    assert "weekly_reports" in tables
    assert "schema_migrations" in tables
    assert status["up_to_date"] is True


def test_init_db_does_not_delete_existing_data():
    app = make_app()
    with app.app_context():
        db = get_db()
        db.execute(
            """
            INSERT INTO foods
                (name, portion_grams, calories, protein_g, carbs_g, fat_g, fiber_g)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("Alimento preservado", 100, 100, 10, 10, 1, 2),
        )
        db.commit()

        init_db()

        food = db.execute(
            "SELECT name FROM foods WHERE name = ?",
            ("Alimento preservado",),
        ).fetchone()

    assert food is not None


def test_apply_single_migration_registers_version():
    db = memory_db()
    migrations_dir = make_artifact_dir("single-migration")
    try:
        migration = migrations_dir / "001_create_table.sql"
        migration.write_text(
            "CREATE TABLE sample_table (id INTEGER PRIMARY KEY);",
            encoding="utf-8",
        )

        applied = apply_migration(db, migration)
        applied_rows = get_applied_migrations(db)

        assert applied.version == "001"
        assert applied_rows[0]["name"] == "create_table"
    finally:
        shutil.rmtree(migrations_dir, ignore_errors=True)


def test_scripts_status_and_migrate_execute_with_test_database():
    env = os.environ.copy()
    env["NUTRITRACK_DATABASE"] = ":memory:"
    env["NUTRITRACK_AUTH_ENABLED"] = "false"

    status_before = subprocess.run(
        [sys.executable, "scripts/db_status.py"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    migrate = subprocess.run(
        [sys.executable, "scripts/db_migrate.py"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Pendentes:" in status_before.stdout
    assert "Migracoes aplicadas:" in migrate.stdout
