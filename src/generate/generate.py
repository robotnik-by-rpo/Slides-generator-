import subprocess
from pathlib import Path

def convert_to_marp(input_file: Path, format_p: str):
    """
    Public function for converting .marp.file to pdf/pptx file
    """
    def to_pdf()->list:
        return ['marp', input_file, '--pdf', '-o', "presentation.pdf"]
    def to_pptx()->list:
        return ['marp', input_file, '--pptx', '-o', "presentation.pptx"]
    if format_p == "pdf":
        subprocess.run(to_pdf(), check=True, stderr=subprocess.DEVNULL) 
    elif format_p == "pptx":
        subprocess.run(to_pptx(), check=True, stderr=subprocess.DEVNULL)
    elif format_p == "both":
        subprocess.run(to_pptx(), check=True, stderr=subprocess.DEVNULL)
        subprocess.run(to_pdf(), check=True, stderr=subprocess.DEVNULL) 
