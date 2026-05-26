import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # noqa: E402
from app.database import get_db  # noqa: E402
from app.services.backup_service import BackupError, create_sqlite_backup  # noqa: E402
from app.services.migration_service import (  # noqa: E402
    apply_pending_migrations,
    get_pending_migrations,
)


def main():
    app = create_app({"SKIP_DB_INIT": True})
    database_path = Path(app.config["DATABASE"])

    with app.app_context():
        db = get_db()
        pending = get_pending_migrations(db)

        if not pending:
            print("Nenhuma migracao pendente.")
            return

        if database_path != Path(":memory:") and database_path.exists():
            try:
                backup_path = create_sqlite_backup(database_path)
                print(f"Backup criado antes da migracao: {backup_path.name}")
            except BackupError as exc:
                print(f"Aviso: backup nao criado: {exc}")

        applied = apply_pending_migrations(db)

    print("Migracoes aplicadas:")
    for migration in applied:
        print(f"- {migration.version} {migration.name}")


if __name__ == "__main__":
    main()
