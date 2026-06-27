# tests/test_parse/conftest.py
"""
Pytest configuration and fixtures for parse module tests
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock
from parse.parse import ParserMD

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_lesson_file(temp_dir):
    """Create a sample lesson markdown file"""
    content = """# Introduction to Programming

## Python Basics

Python is a high-level programming language.

## Variables

In Python, variables are created automatically.

## Examples

Code example needed here.
"""
    file_path = temp_dir / "lesson.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "test_api_key_12345"

@pytest.fixture
def parser_md(temp_dir, sample_lesson_file, mock_api_key):
    """Create a ParserMD instance with mock API key"""
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    return ParserMD(sample_lesson_file, output_dir, "default", mock_api_key)

@pytest.fixture
def mock_groq_response():
    """Mock successful Groq API response"""
    return {
        "choices": [
            {
                "message": {
                    "content": """---
marp: true
theme: default
size: 16:9
paginate: true
---

# Introduction to Programming

## Python Basics

Python is a high-level programming language.

## Variables

In Python, variables are created automatically.

---
## Examples

TODO: Add code example for variables
"""
                }
            }
        ]
    }