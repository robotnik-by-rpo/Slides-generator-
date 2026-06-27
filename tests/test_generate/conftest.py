import pytest
from pathlib import Path

@pytest.fixture
def sample_input_file(tmp_path):
    """Fixture to create a temporary .marp file"""
    input_file = tmp_path / "test.marp"
    content = """# Test Presentation

## Introduction
This is a test presentation

## Main Content
- Point 1
- Point 2

## Conclusion
Thank you!
"""
    input_file.write_text(content)
    return input_file

@pytest.fixture
def sample_input_file_empty(tmp_path):
    """Fixture to create an empty file"""
    input_file = tmp_path / "empty.marp"
    input_file.write_text("")
    return input_file