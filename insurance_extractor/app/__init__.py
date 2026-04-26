from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    base_dir = getattr(config_class, "BASE_DIR", Config.BASE_DIR)
    app = Flask(__name__, instance_path=str(base_dir / "instance"))
    app.config.from_object(config_class)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    from .routes import main_bp

    app.register_blueprint(main_bp)

    # For the MVP we create tables automatically, so a beginner can run the
    # project without learning migrations first.
    with app.app_context():
        db.create_all()

    return app
