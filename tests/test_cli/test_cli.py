import sys
from unittest.mock import patch, MagicMock
from src.__main__ import CLI
import json


def test_main_no_args(cli_instance, monkeypatch):
    """Calling without arguments should print error."""
    with patch.object(sys, 'argv', ['script']):
        with patch('builtins.print') as mock_print:
            ret = cli_instance.main()
            assert ret == 1
            mock_print.assert_any_call("Either --plan or --update must be specified")


def test_main_both_args(cli_instance, monkeypatch):
    """Using both --plan and --update should error."""
    with patch.object(sys, 'argv', ['script', '--plan', 'plan.md', '--update', 'dir']):
        with patch('builtins.print') as mock_print:
            ret = cli_instance.main()
            assert ret == 1
            mock_print.assert_any_call("Error: --update and --plan cannot be used together")


@patch('src.__main__.ParserMD')
@patch('src.__main__.convert_to_marp')
@patch('src.__main__.send_next_cloud')
@patch('src.__main__.save_json_metadata')
@patch('src.__main__.send_lrs')
def test_main_generation_all_formats(mock_send_lrs, mock_save_json, mock_send_nextcloud,
                                      mock_convert, mock_parser_md, cli_instance, temp_plan_file, tmp_path):
    """Successful generation of presentation in all formats."""
    mock_parser_instance = MagicMock()
    mock_parser_instance.Parse_file_to_marp.return_value = tmp_path / "plan.marp.md"
    mock_parser_instance.title = "Test Lesson Plan"
    mock_parser_md.return_value = mock_parser_instance

    mock_send_nextcloud.return_value = {
        "plan": "http://fake/plan.md",
        "metadata": "http://fake/metadata.json",
        "pdf": "http://fake/test.pdf",
        "pptx": "http://fake/test.pptx",
        "html": "http://fake/test.html",
    }

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch.object(sys, 'argv', ['script', '--plan', str(temp_plan_file), 
                                    '--output', str(output_dir), '--format', 'all']):
        ret = cli_instance.main()
        assert ret == 0

    mock_parser_md.assert_called_once_with(temp_plan_file, output_dir, "default", "fake-api-key")
    mock_convert.assert_called_once()
    mock_send_nextcloud.assert_called_once()
    
    remote_folder = mock_send_nextcloud.call_args[0][1]
    assert remote_folder == "/slides/output"
    
    local_files = mock_send_nextcloud.call_args[0][0]
    assert "plan" in local_files
    assert "metadata" in local_files
    assert "pdf" in local_files
    assert "pptx" in local_files
    assert "html" in local_files
    
    mock_save_json.assert_called_once()
    mock_send_lrs.assert_called_once()


@patch('src.__main__.ParserMD')
@patch('src.__main__.convert_to_marp')
@patch('src.__main__.send_next_cloud')
@patch('src.__main__.save_json_metadata')
@patch('src.__main__.send_lrs')
def test_main_generation_pdf_only(mock_send_lrs, mock_save_json, mock_send_nextcloud,
                                   mock_convert, mock_parser_md, cli_instance, temp_plan_file, tmp_path):
    """Successful generation of presentation in PDF only."""
    mock_parser_instance = MagicMock()
    mock_parser_instance.Parse_file_to_marp.return_value = tmp_path / "plan.marp.md"
    mock_parser_instance.title = "Test Lesson Plan"
    mock_parser_md.return_value = mock_parser_instance

    mock_send_nextcloud.return_value = {
        "plan": "http://fake/plan.md",
        "metadata": "http://fake/metadata.json",
        "pdf": "http://fake/test.pdf",
    }

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch.object(sys, 'argv', ['script', '--plan', str(temp_plan_file), 
                                    '--output', str(output_dir), '--format', 'pdf']):
        ret = cli_instance.main()
        assert ret == 0

    local_files = mock_send_nextcloud.call_args[0][0]
    assert "pdf" in local_files
    assert "pptx" not in local_files
    assert "html" not in local_files


@patch('src.__main__.ParserMD')
@patch('src.__main__.convert_to_marp')
@patch('src.__main__.send_next_cloud')
@patch('src.__main__.save_json_metadata')
@patch('src.__main__.send_lrs')
def test_main_generation_with_title_sanitization(mock_send_lrs, mock_save_json, mock_send_nextcloud,
                                                  mock_convert, mock_parser_md, cli_instance, 
                                                  temp_plan_file, tmp_path):
    """Test that title with special characters is properly sanitized."""
    mock_parser_instance = MagicMock()
    mock_parser_instance.Parse_file_to_marp.return_value = tmp_path / "plan.marp.md"
    mock_parser_instance.title = "My Test!@# Lesson"
    mock_parser_md.return_value = mock_parser_instance

    mock_send_nextcloud.return_value = {
        "plan": "http://fake/plan.md",
        "metadata": "http://fake/metadata.json",
        "pdf": "http://fake/test.pdf",
    }

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch.object(sys, 'argv', ['script', '--plan', str(temp_plan_file), 
                                    '--output', str(output_dir), '--format', 'pdf']):
        ret = cli_instance.main()
        assert ret == 0

    local_files = mock_send_nextcloud.call_args[0][0]
    pdf_path = local_files["pdf"]
    
    assert "My_Test" in pdf_path
    assert "Lesson" in pdf_path
    assert "!" not in pdf_path
    assert "@" not in pdf_path
    assert "#" not in pdf_path
    assert pdf_path.endswith(".pdf")


@patch('src.__main__.convert_to_marp')
@patch('src.__main__.send_next_cloud')
@patch('src.__main__.save_json_metadata')
@patch('src.__main__.send_lrs')
def test_process_update_mode_all_formats(mock_send_lrs, mock_save_json, mock_send_nextcloud,
                                          mock_convert, cli_instance, update_directory):
    """Update mode should regenerate presentations and upload files in all formats."""
    ret = cli_instance.process_update_mode(update_directory, "all")
    assert ret == 0

    mock_convert.assert_called_once()
    mock_send_nextcloud.assert_called_once()
    
    local_files = mock_send_nextcloud.call_args[0][0]
    assert "metadata" in local_files
    assert "pdf" in local_files
    assert "pptx" in local_files
    assert "html" in local_files
    
    mock_save_json.assert_called_once()
    mock_send_lrs.assert_called_once()


@patch('src.__main__.convert_to_marp')
@patch('src.__main__.send_next_cloud')
@patch('src.__main__.save_json_metadata')
@patch('src.__main__.send_lrs')
def test_process_update_mode_pdf_only(mock_send_lrs, mock_save_json, mock_send_nextcloud,
                                       mock_convert, cli_instance, update_directory):
    """Update mode should regenerate presentations and upload files in PDF only."""
    ret = cli_instance.process_update_mode(update_directory, "pdf")
    assert ret == 0

    local_files = mock_send_nextcloud.call_args[0][0]
    assert "metadata" in local_files
    assert "pdf" in local_files
    assert "pptx" not in local_files
    assert "html" not in local_files


def test_process_update_mode_no_metadata(cli_instance, tmp_path, marp_file_with_title):
    """Update when metadata.json is missing should still work with empty URLs."""
    update_dir = tmp_path / "update_dir"
    update_dir.mkdir()
    target_marp = update_dir / marp_file_with_title.name
    target_marp.write_text(marp_file_with_title.read_text(), encoding='utf-8')

    with patch('src.__main__.convert_to_marp') as mock_convert:
        with patch('src.__main__.send_next_cloud') as mock_send_nc:
            with patch('src.__main__.save_json_metadata') as mock_save:
                with patch('src.__main__.send_lrs'):
                    ret = cli_instance.process_update_mode(update_dir, "all")
                    assert ret == 0
                    saved_xapi = mock_save.call_args[0][0]
                    extensions = saved_xapi["context"]["extensions"]
                    assert extensions["plan_url"] == ""
                    assert extensions["slides_url_pdf"] == ""
                    assert extensions["slides_url_pptx"] == ""
                    assert extensions["slides_url_html"] == ""


def test_process_update_mode_no_marp_files(cli_instance, tmp_path):
    """Update when no .marp.md files exist should return error."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    
    ret = cli_instance.process_update_mode(empty_dir, "all")
    assert ret == 1


def test_extract_title_from_marp(cli_instance, marp_file_with_title):
    """Extract title from .marp.md file."""
    title = cli_instance._extract_title_from_marp(marp_file_with_title)
    assert title == "My Title"


def test_extract_title_from_marp_no_title(cli_instance, tmp_path):
    """Extract title from .marp.md file with no title."""
    marp_file = tmp_path / "test.marp.md"
    marp_file.write_text("""---
marp: true
---
Content without title
""", encoding='utf-8')
    title = cli_instance._extract_title_from_marp(marp_file)
    assert title == "test"


def test_get_plan_from_metadata(cli_instance, tmp_path):
    """Extract extensions from metadata.json."""
    metadata = {
        "context": {
            "extensions": {
                "plan_url": "http://plan",
                "slides_url_pdf": "http://pdf",
                "slides_url_pptx": "http://pptx",
                "slides_url_html": "http://html"
            }
        }
    }
    metadata_path = tmp_path / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f)
    
    extensions = cli_instance._get_plan_from_metadata(metadata_path)
    assert extensions["plan_url"] == "http://plan"
    assert extensions["slides_url_pdf"] == "http://pdf"
    assert extensions["slides_url_pptx"] == "http://pptx"
    assert extensions["slides_url_html"] == "http://html"

    missing = tmp_path / "missing.json"
    assert cli_instance._get_plan_from_metadata(missing) == {}