"""
This is package for parsing markdown files.
"""
from pathlib import Path
from typing import Generator, Optional
def Parse_file_to_marp(path_lesson: Path, path_presentation: Path)-> None:
    generator = __open_file(path_lesson)
    __write_file(path_presentation, generator)

def __open_file(path_lesson: Path) -> Generator[str, None, None]:
    """
    Private function for reading rows from .md file
    
    Args:
        path_lesson: Path to source .md file
    """
    with open(path_lesson, "r", encoding="utf-8") as lesson:
        for row in lesson:
            row = row.strip()
            yield row

def __write_file(path_presentation: Path, rows_generator: Generator[str, None, None])->None:
    """
    Private function for writing rows to .md file
    
    Args:
        path_presentation: Path to export 

    """
    
    with open(path_presentation, "w", encoding="utf-8") as present:
        for row in present:
            sharps = row.count("#")
            if sharps == 2:
                present.write("\n---\n")
            present.write(row + "\n")

