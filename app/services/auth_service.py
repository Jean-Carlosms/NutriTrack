from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash


def is_auth_enabled():
    value = current_app.config.get("NUTRITRACK_AUTH_ENABLED", "false")
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def get_configured_username():
    return current_app.config.get("NUTRITRACK_USERNAME", "admin")


def get_configured_password_hash():
    return current_app.config.get("NUTRITRACK_PASSWORD_HASH", "")


def verify_credentials(username, password):
    if not is_auth_enabled():
        return True
    if not username or not password:
        return False
    if username != get_configured_username():
        return False

    password_hash = get_configured_password_hash()
    if not password_hash:
        return False
    return check_password_hash(password_hash, password)


def generate_password_hash_value(password):
    if not password:
        raise ValueError("senha nao pode ser vazia")
    return generate_password_hash(password)
