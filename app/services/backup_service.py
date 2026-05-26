import shutil
from datetime import datetime
from pathlib import Path


class BackupError(Exception):
    pass


def create_sqlite_backup(database_path, backup_dir=None, now=None):
    source = Path(database_path)
    if not source.exists() or not source.is_file():
        raise BackupError("Banco SQLite ainda nao existe para backup.")

    destination_dir = Path(backup_dir) if backup_dir else source.parent / "backups"
    destination_dir.mkdir(parents=True, exist_ok=True)

    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    destination = destination_dir / f"nutritrack_{timestamp}.db"
    suffix = 1
    while destination.exists():
        destination = destination_dir / f"nutritrack_{timestamp}_{suffix}.db"
        suffix += 1

    shutil.copy2(source, destination)
    return destination
