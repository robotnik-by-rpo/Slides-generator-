import pytest
import subprocess
from unittest.mock import patch, MagicMock
from generate.generate import convert_to_marp, sanitize_filename


class TestSanitizeFilename:
    """Tests for the sanitize_filename function"""
    
    def test_sanitize_with_spaces(self):
        """Test sanitizing filename with spaces"""
        result = sanitize_filename("My Presentation File")
        assert result == "My_Presentation_File"
    
    def test_sanitize_with_special_chars(self):
        """Test sanitizing filename with special characters"""
        result = sanitize_filename("Test@#$%File")
        assert result == "Test_File"
    
    def test_sanitize_with_valid_chars(self):
        """Test sanitizing filename with valid characters"""
        result = sanitize_filename("Valid-Name_123")
        assert result == "Valid-Name_123"
    
    def test_sanitize_empty_string(self):
        """Test sanitizing empty string"""
        result = sanitize_filename("")
        assert result == "presentation"
    
    def test_sanitize_only_invalid_chars(self):
        """Test sanitizing string with only invalid characters"""
        result = sanitize_filename("!@#$%^&*()")
        assert result == "presentation"
    
    def test_sanitize_with_leading_trailing_underscores(self):
        """Test sanitizing with leading and trailing underscores"""
        result = sanitize_filename("_test_")
        assert result == "test"


class TestConvertToMarp:
    """Tests for the convert_to_marp function"""
    
    @pytest.fixture
    def sample_input_file(self, tmp_path):
        """Create a temporary file for testing"""
        input_file = tmp_path / "test.marp"
        input_file.write_text("# Test Presentation\n\n---\n\n## Slide 2")
        return input_file
    
    def test_convert_to_pdf_success(self, sample_input_file):
        """Test successful conversion to PDF"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            convert_to_marp(sample_input_file, "pdf")
            
            expected_path = sample_input_file.parent / "test.pdf"
            expected_command = ['marp', sample_input_file, '--pdf', '-o', expected_path]
            mock_run.assert_called_once_with(
                expected_command, 
                check=True, 
                stderr=subprocess.DEVNULL
            )
    
    def test_convert_to_pptx_success(self, sample_input_file):
        """Test successful conversion to PPTX"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            convert_to_marp(sample_input_file, "pptx")
            
            expected_path = sample_input_file.parent / "test.pptx"
            expected_command = ['marp', sample_input_file, '--pptx', '-o', expected_path]
            mock_run.assert_called_once_with(
                expected_command, 
                check=True, 
                stderr=subprocess.DEVNULL
            )
    
    def test_convert_to_html_success(self, sample_input_file):
        """Test successful conversion to HTML"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            convert_to_marp(sample_input_file, "html")
            
            expected_path = sample_input_file.parent / "test.html"
            expected_command = ['marp', sample_input_file, '--html', '-o', expected_path]
            mock_run.assert_called_once_with(
                expected_command, 
                check=True, 
                stderr=subprocess.DEVNULL
            )
    
    def test_convert_to_all_formats_success(self, sample_input_file):
        """Test successful conversion to all formats"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            convert_to_marp(sample_input_file, "all")
            
            assert mock_run.call_count == 3
            
            expected_pdf_path = sample_input_file.parent / "test.pdf"
            expected_pptx_path = sample_input_file.parent / "test.pptx"
            expected_html_path = sample_input_file.parent / "test.html"
            
            expected_pdf = ['marp', sample_input_file, '--pdf', '-o', expected_pdf_path]
            expected_pptx = ['marp', sample_input_file, '--pptx', '-o', expected_pptx_path]
            expected_html = ['marp', sample_input_file, '--html', '-o', expected_html_path]
            
            mock_run.assert_any_call(expected_pdf, check=True, stderr=subprocess.DEVNULL)
            mock_run.assert_any_call(expected_pptx, check=True, stderr=subprocess.DEVNULL)
            mock_run.assert_any_call(expected_html, check=True, stderr=subprocess.DEVNULL)
    
    def test_convert_with_custom_name(self, sample_input_file, tmp_path):
        """Test conversion with custom base_name and output_dir"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            custom_dir = tmp_path / "output"
            custom_dir.mkdir()
            
            convert_to_marp(
                sample_input_file, 
                "pdf", 
                output_dir=custom_dir,
                base_name="Custom Name With Spaces"
            )
            
            expected_path = custom_dir / "Custom_Name_With_Spaces.pdf"
            expected_command = ['marp', sample_input_file, '--pdf', '-o', expected_path]
            mock_run.assert_called_once_with(
                expected_command,
                check=True,
                stderr=subprocess.DEVNULL
            )
    
    def test_convert_with_custom_name_clean(self, sample_input_file, tmp_path):
        """Test conversion with custom clean base_name"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            custom_dir = tmp_path / "output"
            custom_dir.mkdir()
            
            convert_to_marp(
                sample_input_file, 
                "pdf", 
                output_dir=custom_dir,
                base_name="clean_name"
            )
            
            expected_path = custom_dir / "clean_name.pdf"
            expected_command = ['marp', sample_input_file, '--pdf', '-o', expected_path]
            mock_run.assert_called_once_with(
                expected_command,
                check=True,
                stderr=subprocess.DEVNULL
            )
    
    def test_convert_with_error(self, sample_input_file):
        """Test error handling during conversion"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, 'marp')
            
            with pytest.raises(subprocess.CalledProcessError):
                convert_to_marp(sample_input_file, "pdf")
    
    def test_invalid_format(self, sample_input_file):
        """Test handling of unknown format"""
        with patch('subprocess.run') as mock_run:
            convert_to_marp(sample_input_file, "invalid")
            mock_run.assert_not_called()
    
    def test_convert_from_marp_file_with_extension(self, sample_input_file, tmp_path):
        """Test conversion when input file has .marp.marp extension"""
        input_file = tmp_path / "presentation.marp.marp"
        input_file.write_text("# Test")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            convert_to_marp(input_file, "pdf")
            
            expected_path = tmp_path / "presentation.pdf"
            expected_command = ['marp', input_file, '--pdf', '-o', expected_path]
            mock_run.assert_called_once_with(
                expected_command,
                check=True,
                stderr=subprocess.DEVNULL
            )
    
    def test_convert_with_absolute_path(self, sample_input_file, tmp_path):
        """Test conversion with absolute output directory"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            absolute_dir = tmp_path / "absolute" / "path"
            absolute_dir.mkdir(parents=True)
            
            convert_to_marp(
                sample_input_file, 
                "pdf",
                output_dir=absolute_dir
            )
            
            expected_path = absolute_dir / "test.pdf"
            expected_command = ['marp', sample_input_file, '--pdf', '-o', expected_path]
            mock_run.assert_called_once_with(
                expected_command,
                check=True,
                stderr=subprocess.DEVNULL
            )
    
    def test_convert_multiple_formats_individual_calls(self, sample_input_file):
        """Test converting to multiple formats with individual calls"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            for fmt in ["pdf", "pptx", "html"]:
                convert_to_marp(sample_input_file, fmt)
            
            assert mock_run.call_count == 3
            
            calls = mock_run.call_args_list
            formats_called = []
            for call in calls:
                args = call[0][0]
                if '--pdf' in args:
                    formats_called.append('pdf')
                elif '--pptx' in args:
                    formats_called.append('pptx')
                elif '--html' in args:
                    formats_called.append('html')
            
            assert set(formats_called) == {"pdf", "pptx", "html"}