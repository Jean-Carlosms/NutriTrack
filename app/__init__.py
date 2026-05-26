import os

from flask import Flask

from app.database import close_db, init_db, reset_db
from app.routes import bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get(
            "NUTRITRACK_DATABASE",
            app.instance_path + "/nutritrack.db",
        ),
        NUTRITRACK_AUTH_ENABLED=os.environ.get("NUTRITRACK_AUTH_ENABLED", "false"),
        NUTRITRACK_USERNAME=os.environ.get("NUTRITRACK_USERNAME", "admin"),
        NUTRITRACK_PASSWORD_HASH=os.environ.get("NUTRITRACK_PASSWORD_HASH", ""),
        SKIP_DB_INIT=False,
    )

    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    app.register_blueprint(bp)
    register_cli_commands(app)

    if not app.config["SKIP_DB_INIT"]:
        with app.app_context():
            init_db()

    return app


def register_cli_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Banco SQLite inicializado.")

    @app.cli.command("reset-db")
    def reset_db_command():
        reset_db()
        print("Banco SQLite recriado com dados ficticios.")
