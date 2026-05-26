import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # noqa: E402
from app.database import get_db  # noqa: E402
from app.services.migration_service import get_migration_status  # noqa: E402


def main():
    app = create_app({"SKIP_DB_INIT": True})
    with app.app_context():
        status = get_migration_status(get_db())

    print("Status das migracoes do NutriTrack")
    print(f"Total: {status['total_count']}")
    print(f"Aplicadas: {status['applied_count']}")
    print(f"Pendentes: {status['pending_count']}")

    if status["applied"]:
        print("\nAplicadas:")
        for migration in status["applied"]:
            print(
                f"- {migration['version']} {migration['name']} "
                f"({migration['applied_at']})"
            )

    if status["pending"]:
        print("\nPendentes:")
        for migration in status["pending"]:
            print(f"- {migration.version} {migration.name}")

    if status["up_to_date"]:
        print("\nBanco atualizado.")
    else:
        print("\nExecute: python scripts/db_migrate.py")


if __name__ == "__main__":
    main()
