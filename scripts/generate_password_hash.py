import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.auth_service import generate_password_hash_value


def main():
    if len(sys.argv) != 2 or not sys.argv[1]:
        print('Uso: python scripts/generate_password_hash.py "minha_senha"')
        return 1

    print(f"NUTRITRACK_PASSWORD_HASH={generate_password_hash_value(sys.argv[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
