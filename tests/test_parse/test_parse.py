import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import requests
from parse.parse import ParserMD


class TestParserMDCore:
    """Core tests for ParserMD functionality"""
    
    def test_init(self, temp_dir, sample_lesson_file, mock_api_key):
        """Test valid initialization"""
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        parser = ParserMD(sample_lesson_file, output_dir, "default", mock_api_key)
        
        assert parser.path_lesson == sample_lesson_file
        assert parser.path_presentation == output_dir
        assert parser.theme_marp == "default"
        assert parser.api_key == mock_api_key
    
    def test_load_prompts(self, temp_dir, sample_lesson_file, mock_api_key):
        """Test loading prompts from YAML file"""
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        parser = ParserMD(sample_lesson_file, output_dir, "default", mock_api_key)
        
        assert "system" in parser.prompts
        assert "user_template" in parser.prompts
        assert len(parser.prompts["system"]) > 0
    
    def test_extract_title(self, parser_md):
        """Test title extraction from content"""
        content = "# Main Title\n\nContent here"
        title = parser_md._extract_title(content)
        assert title == "Main Title"
        
        content = "No headers here"
        title = parser_md._extract_title(content)
        assert title == "Presentation"


class TestParserMDWithAI:
    """Tests for AI-powered presentation generation"""
    
    @patch('requests.post')
    def test_generate_presentation_success(self, mock_post, parser_md, mock_groq_response):
        """Test successful presentation generation via Groq API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_groq_response
        mock_post.return_value = mock_response
        
        plan_content = parser_md._read_plan_file()
        result = parser_md._generate_presentation_with_ai(plan_content)
        
        # Verify API call
        mock_post.assert_called_once()
        assert "marp: true" in result
        assert f"theme: {parser_md.theme_marp}" in result
        assert "Introduction to Programming" in result
    
    @patch('requests.post')
    def test_generate_presentation_api_error(self, mock_post, parser_md):
        """Test handling of API errors"""
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        plan_content = parser_md._read_plan_file()
        with pytest.raises(requests.exceptions.RequestException):
            parser_md._generate_presentation_with_ai(plan_content)
    
    def test_generate_presentation_no_api_key(self, temp_dir, sample_lesson_file):
        """Test behavior when API key is missing"""
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        parser = ParserMD(sample_lesson_file, output_dir, "default", "")
        
        plan_content = parser._read_plan_file()
        with pytest.raises(ValueError, match="API key is required"):
            parser._generate_presentation_with_ai(plan_content)
    
    @patch('requests.post')
    def test_parse_file_to_marp_success(self, mock_post, parser_md, temp_dir, mock_groq_response):
        """Test complete file parsing with AI generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_groq_response
        mock_post.return_value = mock_response
        
        result_path = parser_md.parse_file_to_marp()
        
        assert result_path is not None
        assert result_path.exists()
        assert result_path.name == "lesson.marp.md"
        
        content = result_path.read_text(encoding="utf-8")
        assert "marp: true" in content
        assert "Introduction to Programming" in content


class TestParserMDMetadata:
    """Tests for metadata handling"""
    
    def test_add_metadata_when_missing(self, parser_md):
        """Test adding metadata when none exists"""
        content = "# Test Slide\n\nContent here"
        result = parser_md._add_metadata(content)
        
        assert result.startswith("---")
        assert "marp: true" in result
        assert f"theme: {parser_md.theme_marp}" in result
        assert "size: 16:9" in result
    
    def test_add_metadata_when_exists(self, parser_md):
        """Test replacing existing metadata"""
        content = """---
theme: custom
size: 4:3
---
# Test Slide
"""
        result = parser_md._add_metadata(content)
        
        assert "marp: true" in result
        assert f"theme: {parser_md.theme_marp}" in result
        assert "size: 16:9" in result
        assert "theme: custom" not in result
    
    def test_save_marp_file(self, parser_md, temp_dir):
        """Test saving Marp file"""
        content = "# Test Presentation\n\nContent"
        file_path = parser_md._save_marp_file(content)
        
        assert file_path.exists()
        assert file_path.name == "lesson.marp.md"
        
        saved_content = file_path.read_text(encoding="utf-8")
        assert saved_content == content


class TestParserMDEdgeCases:
    """Test edge cases and error handling"""
    
    def test_file_not_found(self, temp_dir, mock_api_key):
        """Test handling of missing file"""
        non_existent = temp_dir / "nonexistent.md"
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        parser = ParserMD(non_existent, output_dir, "default", mock_api_key)
        result = parser.parse_file_to_marp()
        assert result is None
    
    def test_empty_file(self, temp_dir, mock_api_key):
        """Test handling of empty file"""
        file_path = temp_dir / "empty.md"
        file_path.write_text("", encoding="utf-8")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        parser = ParserMD(file_path, output_dir, "default", mock_api_key)
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "# Empty Presentation"}}]
            }
            mock_post.return_value = mock_response
            
            result = parser.parse_file_to_marp()
            assert result is not None
            assert result.exists()
    
    @patch('requests.post')
    def test_api_timeout(self, mock_post, parser_md):
        """Test handling of API timeout"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        plan_content = parser_md._read_plan_file()
        with pytest.raises(requests.exceptions.Timeout):
            parser_md._generate_presentation_with_ai(plan_content)


class TestParserMDIntegration:
    """Integration tests for complete workflow"""
    
    @patch('requests.post')
    def test_full_workflow_preserves_order(self, mock_post, temp_dir, mock_api_key):
        """Test that content order is preserved"""
        content = """# First

## Second

Third content

## Fourth

Fifth content
"""
        file_path = temp_dir / "order.md"
        file_path.write_text(content, encoding="utf-8")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": content}}]
        }
        mock_post.return_value = mock_response
        
        parser = ParserMD(file_path, output_dir, "default", mock_api_key)
        result = parser.parse_file_to_marp()
        
        assert result is not None
        saved_content = result.read_text(encoding="utf-8")
        
        # Check order preserved
        first_idx = saved_content.find("# First")
        second_idx = saved_content.find("## Second")
        third_idx = saved_content.find("Third content")
        fourth_idx = saved_content.find("## Fourth")
        fifth_idx = saved_content.find("Fifth content")
        
        assert first_idx < second_idx < third_idx < fourth_idx < fifth_idx
    
    @patch('requests.post')
    def test_multiple_files_batch(self, mock_post, temp_dir, mock_api_key):
        """Test processing multiple files"""
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        lessons = [
            ("lesson1.md", "# Lesson 1\n\n## Section A\n\nContent A"),
            ("lesson2.md", "# Lesson 2\n\n## Section B\n\nContent B"),
        ]
        
        for filename, content in lessons:
            file_path = temp_dir / filename
            file_path.write_text(content, encoding="utf-8")
            
            mock_response.json.return_value = {
                "choices": [{"message": {"content": content}}]
            }
            mock_post.return_value = mock_response
            
            parser = ParserMD(file_path, output_dir, "default", mock_api_key)
            result = parser.parse_file_to_marp()
            assert result is not None
        
        # Check all files were created
        for filename, _ in lessons:
            marp_file = output_dir / filename.replace(".md", ".marp.md")
            assert marp_file.exists()