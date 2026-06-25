import json
import pytest
from pathlib import Path
from datetime import datetime
from src.metadata.metadata import Save_json_metadata


class TestSaveJsonMetadata:
    """Tests for Save_json_metadata function"""
    
    def test_save_valid_dict(self, tmp_path):
        """Test saving a valid dictionary to JSON file"""
        # Arrange
        data = {
            "actor": {"mbox": "mailto:teacher@example.com"},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/generated"},
            "object": {"id": "urn:lesson:1234"},
            "timestamp": datetime.now().isoformat()
        }
        file_path = tmp_path / "metadata.json"
        
        # Act
        Save_json_metadata(data, file_path)
        
        # Assert
        assert file_path.exists()
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == data
    
    def test_save_with_unicode(self, tmp_path):
        """Test saving with Unicode characters (Cyrillic)"""
        # Arrange
        data = {
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/generated",
                "display": {"ru": "сгенерировал презентацию"}
            },
            "object": {
                "definition": {
                    "name": {"ru": "Урок 1: Введение в Python"}
                }
            }
        }
        file_path = tmp_path / "unicode_metadata.json"
        
        # Act
        Save_json_metadata(data, file_path)
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == data
        assert "сгенерировал презентацию" in json.dumps(saved_data, ensure_ascii=False)
    
    def test_pretty_formatting(self, tmp_path):
        """Test that JSON is saved with proper indentation (4 spaces)"""
        # Arrange
        data = {"key": "value", "nested": {"inner": "data"}}
        file_path = tmp_path / "pretty.json"
        
        # Act
        Save_json_metadata(data, file_path)
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Verify indentation (4 spaces)
        assert '    "key"' in content
        assert '    "nested"' in content
        assert '        "inner"' in content
    
    def test_empty_dict(self, tmp_path):
        """Test saving an empty dictionary"""
        # Arrange
        data = {}
        file_path = tmp_path / "empty.json"
        
        # Act
        Save_json_metadata(data, file_path)
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == {}
        assert saved_data is not None
    
    def test_nested_structure(self, tmp_path):
        """Test saving complex nested structure (xAPI statement)"""
        # Arrange - xAPI statement
        data = {
            "actor": {
                "mbox": "mailto:teacher@example.com",
                "name": "Иван Петров"
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/generated",
                "display": {
                    "ru": "сгенерировал презентацию",
                    "en": "generated presentation"
                }
            },
            "object": {
                "id": "urn:lesson:1234",
                "definition": {
                    "name": {
                        "ru": "Урок 1: Введение",
                        "en": "Lesson 1: Introduction"
                    },
                    "description": {
                        "ru": "Первый урок курса"
                    }
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
        file_path = tmp_path / "xapi_statement.json"
        
        # Act
        Save_json_metadata(data, file_path)
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == data
        assert saved_data["actor"]["mbox"] == "mailto:teacher@example.com"
        assert saved_data["context"]["extensions"]["plan_url"] == "https://nextcloud/example/lesson1.md"
    
    def test_file_overwrite(self, tmp_path):
        """Test overwriting an existing file"""
        # Arrange
        file_path = tmp_path / "overwrite.json"
        initial_data = {"initial": "data"}
        new_data = {"new": "data"}
        
        # Act - first write
        Save_json_metadata(initial_data, file_path)
        # Act - overwrite
        Save_json_metadata(new_data, file_path)
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == new_data
        assert saved_data != initial_data
    
    def test_special_types_converted(self, tmp_path):
        """Test that special types are properly converted to JSON"""
        # Arrange
        data = {
            "bool_true": True,
            "bool_false": False,
            "none_value": None,
            "int_value": 42,
            "float_value": 3.14,
            "list_value": [1, 2, 3],
            "tuple_value": (1, 2, 3)  # tuple becomes list in JSON
        }
        file_path = tmp_path / "types.json"
        
        # Act
        Save_json_metadata(data, file_path)
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data["bool_true"] is True
        assert saved_data["bool_false"] is False
        assert saved_data["none_value"] is None
        assert saved_data["int_value"] == 42
        assert saved_data["float_value"] == 3.14
        assert saved_data["list_value"] == [1, 2, 3]
        assert saved_data["tuple_value"] == [1, 2, 3]  # tuple converted to list


class TestSaveJsonMetadataErrors:
    """Error handling tests for Save_json_metadata"""
    
    def test_unserializable_object(self, tmp_path):
        """Test that unserializable objects raise TypeError"""
        # Arrange
        class CustomClass:
            def __init__(self, value):
                self.value = value
        
        data = {
            "custom": CustomClass("test")  # Unserializable object
        }
        file_path = tmp_path / "unserializable.json"
        
        # Assert
        with pytest.raises(TypeError):
            Save_json_metadata(data, file_path)
    
    def test_unserializable_set(self, tmp_path):
        """Test that sets (unserializable) raise TypeError"""
        # Arrange
        data = {
            "set_value": {1, 2, 3}  # Set is not JSON serializable
        }
        file_path = tmp_path / "set_error.json"
        
        # Assert
        with pytest.raises(TypeError):
            Save_json_metadata(data, file_path)
    
    def test_invalid_file_path(self):
        """Test that invalid file path raises FileNotFoundError"""
        # Arrange
        data = {"test": "data"}
        # Path to a non-existent directory
        invalid_path = Path("/nonexistent/directory/file.json")
        
        # Assert
        with pytest.raises(FileNotFoundError):
            Save_json_metadata(data, invalid_path)


class TestSaveJsonMetadataIntegration:
    """Integration tests with xAPI statements"""
    
    def test_full_xapi_statement(self, tmp_path):
        """Test saving a complete xAPI statement"""
        # Arrange
        xapi_statement = {
            "actor": {
                "mbox": "mailto:teacher@example.com",
                "name": "Иван Петров",
                "objectType": "Agent"
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/generated",
                "display": {
                    "ru": "сгенерировал презентацию",
                    "en": "generated presentation"
                }
            },
            "object": {
                "id": "urn:lesson:1234",
                "definition": {
                    "name": {
                        "ru": "Урок 1: Введение в Python",
                        "en": "Lesson 1: Introduction to Python"
                    },
                    "description": {
                        "ru": "Первый урок курса по Python",
                        "en": "First lesson of Python course"
                    }
                },
                "objectType": "Activity"
            },
            "context": {
                "extensions": {
                    "course_id": "python_basics_2026",
                    "plan_version": "1.0",
                    "plan_url": "https://nextcloud/example/lesson1.md",
                    "slides_url": "https://nextcloud/example/lesson1.pdf"
                },
                "contextActivities": {
                    "parent": [{
                        "id": "urn:course:python_basics",
                        "definition": {
                            "name": {"ru": "Python для начинающих"}
                        }
                    }]
                }
            },
            "timestamp": "2026-06-25T12:00:00+03:00",
            "version": "1.0.0"
        }
        file_path = tmp_path / "xapi_full_statement.json"
        
        # Act
        Save_json_metadata(xapi_statement, file_path)
        
        # Assert
        assert file_path.exists()
        with open(file_path, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        
        # Verify structure
        assert "actor" in saved
        assert "verb" in saved
        assert "object" in saved
        assert "context" in saved
        assert "timestamp" in saved
        assert saved["actor"]["mbox"] == "mailto:teacher@example.com"
        assert "generated" in saved["verb"]["id"]
    
    def test_multiple_metadata_files(self, tmp_path):
        """Test saving multiple metadata files"""
        # Arrange
        statements = [
            {"id": 1, "data": "first"},
            {"id": 2, "data": "second"},
            {"id": 3, "data": "third"}
        ]
        
        # Act
        for i, statement in enumerate(statements):
            file_path = tmp_path / f"statement_{i}.json"
            Save_json_metadata(statement, file_path)
        
        # Assert
        for i in range(3):
            file_path = tmp_path / f"statement_{i}.json"
            assert file_path.exists()
            with open(file_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            assert saved["id"] == i + 1
    
    def test_xapi_example_from_spec(self, tmp_path):
        """Test saving the xAPI example from the specification"""
        # Arrange - data from the provided example
        xapi_data = {
            "actor": {"mbox": "mailto:teacher@example.com"},
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/generated",
                "display": {"ru": "сгенерировал презентацию"}
            },
            "object": {
                "id": "urn:lesson:1234",
                "definition": {"name": {"ru": "Урок 1: Введение"}}
            },
            "context": {
                "extensions": {
                    "plan_url": "https://nextcloud/.../lesson1.md",
                    "slides_url": "https://nextcloud/.../lesson1.pdf"
                }
            }
        }
        file_path = tmp_path / "xapi_example.json"
        
        # Act
        Save_json_metadata(xapi_data, file_path)
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        
        assert saved["actor"]["mbox"] == "mailto:teacher@example.com"
        assert "generated" in saved["verb"]["id"]
        assert saved["object"]["id"] == "urn:lesson:1234"
        assert "plan_url" in saved["context"]["extensions"]
        assert "slides_url" in saved["context"]["extensions"]


# Fixtures for tests (can be moved to conftest.py)
@pytest.fixture
def sample_xapi_data():
    """Fixture with sample xAPI data"""
    return {
        "actor": {"mbox": "mailto:teacher@example.com"},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/generated"},
        "object": {"id": "urn:lesson:1234"},
        "timestamp": "2026-06-25T12:00:00"
    }