import shutil
from pathlib import Path

import pytest

from app import create_app, db
from app.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = str(Path(__file__).resolve().parent / "tmp_uploads")


@pytest.fixture()
def app():
    test_app = create_app(TestConfig)
    upload_folder = Path(test_app.config["UPLOAD_FOLDER"])

    with test_app.app_context():
        db.drop_all()
        db.create_all()

    yield test_app

    shutil.rmtree(upload_folder, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()
