import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Fixture that creates a temporary directory and cleans up after tests"""
    dir_path = Path(tempfile.mkdtemp())
    yield dir_path
    # Cleanup after tests
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def test_metadata_dir(temp_dir):
    """Fixture providing a path to metadata directory"""
    metadata_dir = temp_dir / "metadata"
    metadata_dir.mkdir(exist_ok=True)
    return metadata_dir


@pytest.fixture
def sample_lesson_metadata():
    """Fixture with lesson metadata"""
    return {
        "lesson_id": "lesson_001",
        "lesson_name": "Introduction to Python",
        "author": "Ivan Petrov",
        "created_at": "2026-06-25T12:00:00",
        "slides_count": 15,
        "topics": ["Variables", "Data Types", "Conditional Operators"]
    }


@pytest.fixture
def sample_xapi_statement():
    """Fixture with xAPI statement"""
    return {
        "actor": {
            "mbox": "mailto:teacher@example.com",
            "name": "Ivan Petrov"
        },
        "verb": {
            "id": "http://adlnet.gov/expapi/verbs/generated",
            "display": {
                "ru": "сгенерировал презентацию"
            }
        },
        "object": {
            "id": "urn:lesson:1234",
            "definition": {
                "name": {"ru": "Урок 1: Введение"}
            }
        },
        "context": {
            "extensions": {
                "plan_url": "https://nextcloud/example/lesson1.md",
                "slides_url": "https://nextcloud/example/lesson1.pdf"
            }
        },
        "timestamp": "2026-06-25T12:00:00"
    }

@pytest.fixture
def sample_xapi_data():
    """Fixture with sample xAPI data"""
    return {
        "actor": {"mbox": "mailto:teacher@example.com"},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/generated"},
        "object": {"id": "urn:lesson:1234"},
        "timestamp": "2026-06-25T12:00:00"
    }