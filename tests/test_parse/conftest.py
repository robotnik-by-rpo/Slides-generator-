"""
Pytest configuration and fixtures for parse module tests
"""
import pytest
from pathlib import Path
import tempfile
import shutil
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
    content = """# Введение в программирование

## Основы Python

Python - это высокоуровневый язык программирования.

## Переменные и типы данных

В Python переменные создаются автоматически.

## Примеры

Здесь нужен пример кода.

## Итоги

Краткое резюме урока.
"""
    file_path = temp_dir / "lesson.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

@pytest.fixture
def lesson_with_todos_file(temp_dir):
    """Create a lesson file with content that should trigger TODOs"""
    content = """# Урок по анализу данных

## Введение

В этом уроке мы рассмотрим анализ данных.

## Схема работы

Нужна схема процесса анализа данных.

## Примеры

Приведите примеры использования.
"""
    file_path = temp_dir / "lesson_todos.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

@pytest.fixture
def parser_md(temp_dir, sample_lesson_file):
    """Create a ParserMD instance"""
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    return ParserMD(sample_lesson_file, output_dir, "default")