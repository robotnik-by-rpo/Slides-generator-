# tests/test_generate/test_generate.py

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.generate.generate import convert_to_marp


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
    
    def test_convert_to_both_success(self, sample_input_file):
        """Test successful conversion to both formats"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            
            convert_to_marp(sample_input_file, "both")
            
            assert mock_run.call_count == 2
            
            expected_pdf_path = sample_input_file.parent / "test.pdf"
            expected_pptx_path = sample_input_file.parent / "test.pptx"
            
            expected_pdf = ['marp', sample_input_file, '--pdf', '-o', expected_pdf_path]
            expected_pptx = ['marp', sample_input_file, '--pptx', '-o', expected_pptx_path]
            
            mock_run.assert_any_call(expected_pdf, check=True, stderr=subprocess.DEVNULL)
            mock_run.assert_any_call(expected_pptx, check=True, stderr=subprocess.DEVNULL)
    
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
                base_name="custom_name"
            )
            
            expected_path = custom_dir / "custom_name.pdf"
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