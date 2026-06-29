import pytest
import json
from src.__main__ import CLI

@pytest.fixture
def temp_plan_file(tmp_path):
    """Create temporary plan file with a title."""
    plan_content = "# Test Lesson Plan\n## Introduction\nSome content"
    plan_file = tmp_path / "plan.md"
    plan_file.write_text(plan_content, encoding='utf-8')
    return plan_file

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    return out_dir

@pytest.fixture
def mock_env(monkeypatch):
    """Set environment variables for testing."""
    env_vars = {
        "SLIDES_OUTPUT_FOLDER": "/fake/output",
        "LRS_ENDPOINT": "http://fake-lrs:8000/xAPI/statements",
        "LOGIN_LRS": "testuser",
        "PASSWORD_LRS": "testpass",
        "API_AI": "fake-api-key",
        "API_NEXTCLOUD": "http://fake-nextcloud:8080",
        "LOGIN_NEXTCLOUD": "admin",
        "PASSWORD_NEXTCLOUD": "admin",
        "FOLDER_NEXTCLOUD": "slides",
        "THEME_MARP": "default",
        "API_KEY_MARP": "fake-marp-key",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

@pytest.fixture
def cli_instance(mock_env):
    """Return an instance of CLI with mocked environment."""
    return CLI()

@pytest.fixture
def marp_file_with_title(tmp_path):
    """Create a .marp.md file with a title."""
    marp = tmp_path / "test.marp.md"
    marp.write_text("""---
marp: true
---
# My Title
Some content
""", encoding='utf-8')
    return marp

@pytest.fixture
def update_directory(tmp_path, marp_file_with_title):
    """Create a directory with .marp.md file and metadata.json."""
    update_dir = tmp_path / "update_dir"
    update_dir.mkdir()
    marp_content = marp_file_with_title.read_text()
    target_marp = update_dir / "test.marp.md"
    target_marp.write_text(marp_content, encoding='utf-8')
    
    metadata = {
        "context": {
            "extensions": {
                "plan_url": "http://fake/plan.md",
                "slides_url_pdf": "http://fake/test.pdf",
                "slides_url_pptx": "http://fake/test.pptx",
            }
        }
    }
    with open(update_dir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f)
    return update_dir