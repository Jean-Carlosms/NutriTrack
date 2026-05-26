from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MIGRATIONS_DIR = PROJECT_ROOT / "migrations"


class MigrationError(Exception):
    pass


@dataclass(frozen=True)
class MigrationFile:
    version: str
    name: str
    path: Path


def ensure_migration_table(db):
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


def parse_migration_file(file_path):
    path = Path(file_path)
    parts = path.stem.split("_", 1)
    if len(parts) != 2 or not parts[0].isdigit():
        raise MigrationError(
            f"Nome de migracao invalido: {path.name}. Use NNN_nome.sql."
        )
    return MigrationFile(version=parts[0], name=parts[1], path=path)


def list_migration_files(migrations_dir=None):
    base_dir = Path(migrations_dir) if migrations_dir else DEFAULT_MIGRATIONS_DIR
    if not base_dir.exists():
        return []

    migrations = [
        parse_migration_file(path)
        for path in base_dir.glob("*.sql")
    ]
    return sorted(migrations, key=lambda migration: migration.version)


def get_applied_migrations(db):
    ensure_migration_table(db)
    rows = db.execute(
        "SELECT version, name, applied_at FROM schema_migrations ORDER BY version"
    ).fetchall()
    return [dict(row) for row in rows]


def get_pending_migrations(db, migrations_dir=None):
    applied_versions = {
        migration["version"]
        for migration in get_applied_migrations(db)
    }
    return [
        migration
        for migration in list_migration_files(migrations_dir)
        if migration.version not in applied_versions
    ]


def sql_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def apply_migration(db, file_path):
    ensure_migration_table(db)
    migration = parse_migration_file(file_path)
    already_applied = db.execute(
        "SELECT 1 FROM schema_migrations WHERE version = ?",
        (migration.version,),
    ).fetchone()
    if already_applied:
        return None

    sql = migration.path.read_text(encoding="utf-8")
    script = f"""
    BEGIN;
    {sql}
    INSERT INTO schema_migrations (version, name)
    VALUES ({sql_literal(migration.version)}, {sql_literal(migration.name)});
    COMMIT;
    """
    try:
        db.executescript(script)
    except Exception as exc:
        try:
            db.executescript("ROLLBACK;")
        except Exception:
            pass
        raise MigrationError(
            f"Falha ao aplicar migracao {migration.path.name}: {exc}"
        ) from exc
    return migration


def apply_pending_migrations(db, migrations_dir=None):
    applied = []
    for migration in get_pending_migrations(db, migrations_dir):
        applied_migration = apply_migration(db, migration.path)
        if applied_migration is not None:
            applied.append(applied_migration)
    return applied


def get_migration_status(db, migrations_dir=None):
    migrations = list_migration_files(migrations_dir)
    applied = get_applied_migrations(db)
    applied_versions = {migration["version"] for migration in applied}
    pending = [
        migration
        for migration in migrations
        if migration.version not in applied_versions
    ]
    return {
        "migrations": migrations,
        "applied": applied,
        "pending": pending,
        "applied_count": len(applied),
        "pending_count": len(pending),
        "total_count": len(migrations),
        "up_to_date": len(pending) == 0,
    }
