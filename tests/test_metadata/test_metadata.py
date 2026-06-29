import json
import pytest
from pathlib import Path
from datetime import datetime
from metadata.metadata import save_json_metadata
from unittest.mock import Mock, patch, MagicMock, ANY
from metadata.metadata import send_lrs, send_next_cloud
import os



class TestSaveJsonMetadata:
    """Tests for save_json_metadata function"""
    
    def test_save_valid_dict(self, tmp_path):
        """Test saving a valid dictionary to JSON file"""
        data = {
            "actor": {"mbox": "mailto:teacher@example.com"},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/generated"},
            "object": {"id": "urn:lesson:1234"},
            "timestamp": datetime.now().isoformat()
        }
        file_path = tmp_path / "metadata.json"
        
        save_json_metadata(data, file_path)
        
        assert file_path.exists()
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == data
    
    def test_save_with_unicode(self, tmp_path):
        """Test saving with Unicode characters (Cyrillic)"""
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
        
        save_json_metadata(data, file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == data
        assert "сгенерировал презентацию" in json.dumps(saved_data, ensure_ascii=False)
    
    def test_pretty_formatting(self, tmp_path):
        """Test that JSON is saved with proper indentation (4 spaces)"""
        data = {"key": "value", "nested": {"inner": "data"}}
        file_path = tmp_path / "pretty.json"
        
        save_json_metadata(data, file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '    "key"' in content
        assert '    "nested"' in content
        assert '        "inner"' in content
    
    def test_empty_dict(self, tmp_path):
        """Test saving an empty dictionary"""
        data = {}
        file_path = tmp_path / "empty.json"
        
        save_json_metadata(data, file_path)
        
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
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/generated",
                "display": {
                    "ru": "сгенерировал презентацию",
                }
            },
            "object": {
                "id": "urn:lesson:1234",
                "definition": {
                    "name": {
                        "ru": "Урок 1: Введение",
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
        save_json_metadata(data, file_path)
        
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
        
        save_json_metadata(initial_data, file_path)
        save_json_metadata(new_data, file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == new_data
        assert saved_data != initial_data
    
    def test_special_types_converted(self, tmp_path):
        """Test that special types are properly converted to JSON"""
        data = {
            "bool_true": True,
            "bool_false": False,
            "none_value": None,
            "int_value": 42,
            "float_value": 3.14,
            "list_value": [1, 2, 3],
            "tuple_value": (1, 2, 3)
        }
        file_path = tmp_path / "types.json"
        
        save_json_metadata(data, file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data["bool_true"] is True
        assert saved_data["bool_false"] is False
        assert saved_data["none_value"] is None
        assert saved_data["int_value"] == 42
        assert saved_data["float_value"] == 3.14
        assert saved_data["list_value"] == [1, 2, 3]
        assert saved_data["tuple_value"] == [1, 2, 3]


class TestSaveJsonMetadataErrors:
    """Error handling tests for save_json_metadata"""
    
    def test_unserializable_object(self, tmp_path):
        """Test that unserializable objects raise TypeError"""
        class CustomClass:
            def __init__(self, value):
                self.value = value
        
        data = {
            "custom": CustomClass("test")
        }
        file_path = tmp_path / "unserializable.json"
        

        with pytest.raises(TypeError):
            save_json_metadata(data, file_path)
    
    def test_unserializable_set(self, tmp_path):
        """Test that sets (unserializable) raise TypeError"""
    
        data = {
            "set_value": {1, 2, 3}
        }
        file_path = tmp_path / "set_error.json"
        
        
        with pytest.raises(TypeError):
            save_json_metadata(data, file_path)
    
    def test_invalid_file_path(self):
        """Test that invalid file path raises FileNotFoundError"""
        data = {"test": "data"}
        invalid_path = Path("/nonexistent/directory/file.json")
    
        with pytest.raises(FileNotFoundError):
            save_json_metadata(data, invalid_path)


class TestSaveJsonMetadataIntegration:
    """Integration tests with xAPI statements"""
    
    def test_full_xapi_statement(self, tmp_path):
        """Test saving a complete xAPI statement"""
        xapi_statement = {
            "actor": {
                "mbox": "mailto:teacher@example.com",
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/generated",
                "display": {
                    "ru": "сгенерировал презентацию",
                }
            },
            "object": {
                "id": "urn:lesson:1234",
                "definition": {
                    "name": {
                        "ru": "Урок 1: Введение в Python",
                    },
                    "description": {
                        "ru": "Первый урок курса по Python",
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
        
    
        save_json_metadata(xapi_statement, file_path)
        
        assert file_path.exists()
        with open(file_path, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        
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
        

        for i, statement in enumerate(statements):
            file_path = tmp_path / f"statement_{i}.json"
            save_json_metadata(statement, file_path)
        
        # Assert
        for i in range(3):
            file_path = tmp_path / f"statement_{i}.json"
            assert file_path.exists()
            with open(file_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            assert saved["id"] == i + 1
    
    def test_xapi_example_from_spec(self, tmp_path):
        """Test saving the xAPI example from the specification"""
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
        
        save_json_metadata(xapi_data, file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        
        assert saved["actor"]["mbox"] == "mailto:teacher@example.com"
        assert "generated" in saved["verb"]["id"]
        assert saved["object"]["id"] == "urn:lesson:1234"
        assert "plan_url" in saved["context"]["extensions"]
        assert "slides_url" in saved["context"]["extensions"]



class TestSendNextCloud:
    """Tests for send_next_cloud function"""
    
    @patch('metadata.metadata.nextcloud_client.Client')
    def test_send_next_cloud_with_all_files(self, mock_client_class, tmp_path):
        """Test successful upload with all three files (plan, pdf, pptx)"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        plan_file = tmp_path / "lesson1.md"
        plan_file.write_text("plan content")
        pdf_file = tmp_path / "lesson1.pdf"
        pdf_file.write_text("pdf content")
        pptx_file = tmp_path / "lesson1.pptx"
        pptx_file.write_text("pptx content")

        path_files = {
            "plan": str(plan_file),
            "pdf": str(pdf_file),
            "pptx": str(pptx_file)
        }
        remote_folder = '/Documents/Lessons'
        with patch.dict(os.environ, {
            'API_NEXTCLOUD': 'https://your-nextcloud.com',
            'LOGIN_NEXTCLOUD': 'test_user',
            'PASSWORD_NEXTCLOUD': 'test_pass',
            'FOLDER_NEXTCLOUD': '/Documents/Lessons/'
        }):
            send_next_cloud(path_files, remote_folder)

        mock_client_class.assert_called_once_with('https://your-nextcloud.com')
        mock_client.login.assert_called_once_with('test_user', 'test_pass')
        assert mock_client.put_file.call_count == 3
        mock_client.put_file.assert_any_call(f"/Documents/Lessons/{plan_file.name}", str(plan_file))
        mock_client.put_file.assert_any_call(f"/Documents/Lessons/{pdf_file.name}", str(pdf_file))
        mock_client.put_file.assert_any_call(f"/Documents/Lessons/{pptx_file.name}", str(pptx_file))

    @patch('metadata.metadata.nextcloud_client.Client')
    def test_send_next_cloud_with_plan_only(self, mock_client_class, tmp_path):
        """Test successful upload with only plan file"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        plan_file = tmp_path / "lesson1.md"
        plan_file.write_text("plan content")

        path_files = {"plan": str(plan_file)}
        remote_folder = '/Documents/Lessons'
        with patch.dict(os.environ, {
            'API_NEXTCLOUD': 'https://your-nextcloud.com',
            'LOGIN_NEXTCLOUD': 'test_user',
            'PASSWORD_NEXTCLOUD': 'test_pass',
            'FOLDER_NEXTCLOUD': '/Documents/Lessons/'
        }):
            send_next_cloud(path_files, remote_folder)

        mock_client.login.assert_called_once()
        assert mock_client.put_file.call_count == 1
        mock_client.put_file.assert_called_once_with(f"/Documents/Lessons/{plan_file.name}", str(plan_file))

    @patch('metadata.metadata.nextcloud_client.Client')
    def test_send_next_cloud_with_plan_and_pdf(self, mock_client_class, tmp_path):
        """Test successful upload with plan and pdf files"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        plan_file = tmp_path / "lesson1.md"
        plan_file.write_text("plan content")
        pdf_file = tmp_path / "lesson1.pdf"
        pdf_file.write_text("pdf content")

        path_files = {"plan": str(plan_file), "pdf": str(pdf_file)}
        remote_folder = '/Documents/Lessons'
        with patch.dict(os.environ, {
            'API_NEXTCLOUD': 'https://your-nextcloud.com',
            'LOGIN_NEXTCLOUD': 'test_user',
            'PASSWORD_NEXTCLOUD': 'test_pass',
            'FOLDER_NEXTCLOUD': '/Documents/Lessons/'
        }):
            send_next_cloud(path_files, remote_folder)

        assert mock_client.put_file.call_count == 2
        mock_client.put_file.assert_any_call(f"/Documents/Lessons/{plan_file.name}", str(plan_file))
        mock_client.put_file.assert_any_call(f"/Documents/Lessons/{pdf_file.name}", str(pdf_file))

    @patch('metadata.metadata.nextcloud_client.Client')
    def test_send_next_cloud_with_plan_and_pptx(self, mock_client_class, tmp_path):
        """Test successful upload with plan and pptx files"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        plan_file = tmp_path / "lesson1.md"
        plan_file.write_text("plan content")
        pptx_file = tmp_path / "lesson1.pptx"
        pptx_file.write_text("pptx content")

        path_files = {"plan": str(plan_file), "pptx": str(pptx_file)}
        remote_folder = '/Documents/Lessons'
        with patch.dict(os.environ, {
            'API_NEXTCLOUD': 'https://your-nextcloud.com',
            'LOGIN_NEXTCLOUD': 'test_user',
            'PASSWORD_NEXTCLOUD': 'test_pass',
            'FOLDER_NEXTCLOUD': '/Documents/Lessons/'
        }):
            send_next_cloud(path_files, remote_folder)

        assert mock_client.put_file.call_count == 2
        mock_client.put_file.assert_any_call(f"/Documents/Lessons/{plan_file.name}", str(plan_file))
        mock_client.put_file.assert_any_call(f"/Documents/Lessons/{pptx_file.name}", str(pptx_file))

    @patch('metadata.metadata.nextcloud_client.Client')
    def test_send_next_cloud_handles_missing_files_gracefully(self, mock_client_class, tmp_path):
        """Test that missing optional files are handled gracefully"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        plan_file = tmp_path / "lesson1.md"
        plan_file.write_text("plan content")

        path_files = {"plan": str(plan_file)}
        remote_folder = '/Documents/Lessons'
        with patch.dict(os.environ, {
            'API_NEXTCLOUD': 'https://your-nextcloud.com',
            'LOGIN_NEXTCLOUD': 'test_user',
            'PASSWORD_NEXTCLOUD': 'test_pass',
            'FOLDER_NEXTCLOUD': '/Documents/Lessons/'
        }):
            send_next_cloud(path_files, remote_folder)

        mock_client.login.assert_called_once()
        assert mock_client.put_file.call_count == 1
        mock_client.put_file.assert_called_once_with(f"/Documents/Lessons/{plan_file.name}", str(plan_file))