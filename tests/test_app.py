import os
import tempfile

import pytest


@pytest.fixture()
def client():
    # Create a temporary SQLite database.
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    os.environ["DATABASE_PATH"] = db_path

    import app as flask_app

    flask_app.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
    )

    flask_app.init_db()

    try:
        with flask_app.app.test_client() as test_client:
            yield test_client
    finally:
        # Close any SQLite connection stored by Flask's
        # application context before deleting the database.
        with flask_app.app.app_context():
            if hasattr(flask_app, "get_db"):
                db = flask_app.get_db()
                db.close()

        try:
            os.unlink(db_path)
        except PermissionError:
            # Windows may temporarily keep the database file locked.
            pass

        os.environ.pop("DATABASE_PATH", None)


def test_main_pages_load(client):
    """Check that the main pages load successfully."""
    response = client.get("/")
    assert response.status_code == 200

    response = client.get("/add")
    assert response.status_code == 200

    response = client.get("/applications")
    assert response.status_code == 200


def test_add_application(client):
    """Check that a new internship application can be added."""
    response = client.post(
        "/add",
        data={
            "company": "Test Company",
            "role": "Python Intern",
            "status": "Applied",
            "location": "Hyderabad",
            "application_date": "2026-10-14",
            "notes": "Test application",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Test Company" in response.data
    assert b"Python Intern" in response.data


def test_health(client):
    """Check the application health endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
