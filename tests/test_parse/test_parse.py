"""
Unit tests for parse.py module - Core functionality only
"""
import pytest
from pathlib import Path
from parse.parse import ParserMD

class TestParserMDCore:
    """Core tests for ParserMD functionality"""
    
    def test_init(self, temp_dir, sample_lesson_file):
        """Test valid initialization"""
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        parser = ParserMD(sample_lesson_file, output_dir, "default")
        
        assert parser.path_lesson == sample_lesson_file
        assert parser.path_presentation == output_dir
        assert parser.theme_marp == "default"
        assert parser.title == ""
    
    def test_open_file(self, parser_md, sample_lesson_file):
        """Test opening a valid file"""
        generator = parser_md._ParserMD__open_file()
        rows = list(generator)
        
        expected_content = sample_lesson_file.read_text(encoding="utf-8").strip().split('\n')
        expected_rows = [line.strip() for line in expected_content if line.strip()]
        
        assert len(rows) == len(expected_rows)
        assert rows == expected_rows
    
    def test_analyze_todos(self, parser_md):
        """Test TODO detection for keywords"""
        test_cases = [
            ("Это схема процесса", True, "изображение"),
            ("Приведем пример использования", True, "пример"),
            ("Вопрос для обсуждения", True, "вопрос"),
            ("Выполните задание", True, "задание"),
            ("Обычный текст", False, None),
        ]
        
        for row, should_have_todo, keyword in test_cases:
            result = parser_md._ParserMD__analyze_content_for_todos(row)
            if should_have_todo:
                assert "TODO" in result
                assert keyword in result.lower()
            else:
                assert "TODO" not in result
                assert result == row
    
    def test_parse_file_to_marp_creates_file(self, parser_md, temp_dir):
        """Test that method creates the output file"""
        output_file = temp_dir / "output" / "lesson.marp.md"
        assert not output_file.exists()
        
        parser_md.Parse_file_to_marp()
        
        assert output_file.exists()
    
    def test_parse_file_to_marp_structure(self, parser_md, temp_dir):
        """Test output file has correct structure"""
        parser_md.Parse_file_to_marp()
        
        output_file = temp_dir / "output" / "lesson.marp.md"
        content = output_file.read_text(encoding="utf-8")
        lines = content.split('\n')
        
        # Check frontmatter
        assert lines[0].strip() == "---"
        assert "theme: default" in lines[1]
        assert "size: 16:9" in lines[2]
        assert lines[3].strip() == "---"
        
        # Check content preserved
        assert "# Введение в программирование" in content
        assert "## Основы Python" in content
        assert "## Переменные и типы данных" in content
    
    def test_parse_file_to_marp_with_todos(self, temp_dir, lesson_with_todos_file):
        """Test that TODOs are inserted correctly"""
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        parser = ParserMD(lesson_with_todos_file, output_dir, "default")
        
        parser.Parse_file_to_marp()
        
        output_file = output_dir / "lesson_todos.marp.md"
        content = output_file.read_text(encoding="utf-8")
        
        # Check content preserved
        assert "# Урок по анализу данных" in content
        assert "## Введение" in content
        assert "## Схема работы" in content
        
        # Check TODOs inserted for keywords
        assert "TODO" in content
        assert "схему" in content
        assert "пример" in content

class TestParserMDEdgeCases:
    """Test edge cases and error handling"""
    
    def test_file_not_found(self, temp_dir):
        """Test handling of missing file"""
        non_existent = temp_dir / "nonexistent.md"
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        with pytest.raises(FileNotFoundError):
            parser = ParserMD(non_existent, output_dir, "default")
            parser.Parse_file_to_marp()
    
    def test_empty_file(self, temp_dir):
        """Test handling of empty file"""
        file_path = temp_dir / "empty.md"
        file_path.write_text("", encoding="utf-8")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        parser = ParserMD(file_path, output_dir, "default")
        parser.Parse_file_to_marp()
        
        output_file = output_dir / "empty.marp.md"
        assert output_file.exists()
        
        content = output_file.read_text(encoding="utf-8")
        # Should only have frontmatter
        assert "---" in content
        assert "theme: default" in content
        assert "size: 16:9" in content
    
    def test_special_characters(self, temp_dir):
        """Test handling of special characters"""
        content = """# Тест с символами

## Спецсимволы: @#$%^&*()

Текст с специальными символами

## Формула: E=mc^2

Схема процесса
"""
        file_path = temp_dir / "special.md"
        file_path.write_text(content, encoding="utf-8")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        parser = ParserMD(file_path, output_dir, "default")
        parser.Parse_file_to_marp()
        
        output_file = output_dir / "special.marp.md"
        assert output_file.exists()
        
        result = output_file.read_text(encoding="utf-8")
        assert "E=mc²" in result
        assert "Схема процесса" in result
        assert "TODO" in result  # Should detect "схема" keyword

class TestParserMDIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_workflow_preserves_order(self, temp_dir):
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
        
        parser = ParserMD(file_path, output_dir, "default")
        parser.Parse_file_to_marp()
        
        output_file = output_dir / "order.marp.md"
        result = output_file.read_text(encoding="utf-8")
        
        # Check order preserved
        first_idx = result.find("# First")
        second_idx = result.find("## Second")
        third_idx = result.find("Third content")
        fourth_idx = result.find("## Fourth")
        fifth_idx = result.find("Fifth content")
        
        assert first_idx < second_idx < third_idx < fourth_idx < fifth_idx
    
    def test_multiple_files_batch(self, temp_dir):
        """Test processing multiple files"""
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        lessons = [
            ("lesson1.md", "# Lesson 1\n\n## Section A\n\nContent A"),
            ("lesson2.md", "# Lesson 2\n\n## Section B\n\nСхема B"),
        ]
        
        for filename, content in lessons:
            file_path = temp_dir / filename
            file_path.write_text(content, encoding="utf-8")
            
            parser = ParserMD(file_path, output_dir, "default")
            parser.Parse_file_to_marp()
        
        # Check all files were created
        for filename, _ in lessons:
            marp_file = output_dir / filename.replace(".md", ".marp.md")
            assert marp_file.exists()
            
            content = marp_file.read_text(encoding="utf-8")
            assert "---" in content
            assert "theme: default" in content