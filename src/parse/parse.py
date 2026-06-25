"""
This is package for parsing markdown files.
"""
from pathlib import Path
from typing import Generator, Optional

class ParserMD:
    def __init__(self,path_lesson: Path, path_presentation: Path, theme: str):
        self.path_lesson = path_lesson
        self.path_presentation = path_presentation
        self.title = ""
        self.theme_marp = theme

    def Parse_file_to_marp(self)-> None:
        generator = self._open_file()
        self._write_file(self.path_presentation, generator)

    def _open_file(self) -> Generator[str, None, None]:
        """
        Private function for reading rows from .md file
        
        Args:
            path_lesson: Path to source .md file
        """
        with open(self.path_lesson, "r", encoding="utf-8") as lesson:
            for row in lesson:
                row = row.strip()
                if row:
                    yield row

    def _write_file(self, path_presentation: Path, rows_generator: Generator[str, None, None])->None:
        """
        Private function for writing rows to .md file
        """
        # creating path for .marp.md file
        marp_file_path = path_presentation / f"{self.path_lesson.stem}.marp.md"
        
        with open(marp_file_path, "w", encoding="utf-8") as present:
            directive = f"---\ntheme: {self.theme_marp}\nsize: 16:9\n---\n\n"
            present.write(directive)
            
            slide_count = 0
            for row in rows_generator:
                sharps = row.count("#")
                
                if sharps == 1:
                    if slide_count > 0:
                        present.write("\n---\n\n")
                    self.title = row.strip()
                    present.write(row + "\n\n")
                    slide_count += 1
                    
                elif sharps == 2:
                    present.write("\n---\n\n")
                    present.write(row + "\n\n")
                    slide_count += 1
                    
                else:
                    row = self.__analyze_content_for_todos(row)
                    present.write(row + "\n")
        
        return marp_file_path

    def _analyze_content_for_todos(self, row: str) -> str:
        """
        String analysis for TODO
        """
        todo_patterns = {
            'image': {
                'keywords': ['схема', 'диаграмма', 'рисунок', 'иллюстрация', 
                            'график', 'фото', 'скриншот'],
                'template': '<TODO: Добавить изображение/схему для "{}">'
            },
            'example': {
                'keywords': ['пример', 'кейс', 'случай', 'демонстрация'],
                'template': '<TODO: Добавить практический пример для "{}">'
            },
            'question': {
                'keywords': ['вопрос', 'обсуждение', 'дискуссия', 'опрос'],
                'template': '<TODO: Сформулировать вопрос для обсуждения: "{}">'
            },
            'exercise': {
                'keywords': ['задание', 'практика', 'упражнение', 'лабораторная'],
                'template': '<TODO: Описать задание подробнее для "{}">'
            },
            'formula': {
                'keywords': ['формула', 'уравнение', 'расчет', 'вычисление'],
                'template': '<TODO: Добавить формулу с пояснениями для "{}">'
            },
            'data': {
                'keywords': ['данные', 'статистика', 'результаты', 'показатели'],
                'template': '<TODO: Добавить числовые данные/график для "{}">'
            }
        }

        
        # Skip empty row
        new_rows = row+'\n'
        for todo_type, config in todo_patterns.items():
            if any(keyword in row.lower() for keyword in config['keywords']):
                # Add TODO after row
                new_rows += config['template'].format(row.strip())
                break
        
        return new_rows