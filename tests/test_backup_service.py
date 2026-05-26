from datetime import datetime
from pathlib import Path
import shutil
import uuid

import pytest

from app.services.backup_service import BackupError, create_sqlite_backup


def make_local_test_dir():
    path = Path("test-artifacts") / f"backup-{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    return path


def test_create_sqlite_backup_when_database_exists():
    workspace = make_local_test_dir()
    try:
        database_path = workspace / "nutritrack.db"
        backup_dir = workspace / "backups"
        database_path.write_bytes(b"sqlite-content")

        backup_path = create_sqlite_backup(
            database_path,
            backup_dir=backup_dir,
            now=datetime(2026, 5, 26, 10, 30, 5),
        )

        assert backup_path == backup_dir / "nutritrack_20260526_103005.db"
        assert backup_path.read_bytes() == b"sqlite-content"
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_create_sqlite_backup_rejects_missing_database():
    workspace = make_local_test_dir()
    try:
        with pytest.raises(BackupError):
            create_sqlite_backup(workspace / "missing.db", backup_dir=workspace / "backups")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_create_sqlite_backup_avoids_overwrite():
    workspace = make_local_test_dir()
    try:
        database_path = workspace / "nutritrack.db"
        backup_dir = workspace / "backups"
        database_path.write_bytes(b"new")
        backup_dir.mkdir()
        existing = backup_dir / "nutritrack_20260526_103005.db"
        existing.write_bytes(b"old")

        backup_path = create_sqlite_backup(
            database_path,
            backup_dir=backup_dir,
            now=datetime(2026, 5, 26, 10, 30, 5),
        )

        assert backup_path == backup_dir / "nutritrack_20260526_103005_1.db"
        assert existing.read_bytes() == b"old"
        assert Path(backup_path).read_bytes() == b"new"
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
