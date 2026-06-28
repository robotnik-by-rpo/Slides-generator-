import subprocess
from pathlib import Path

def convert_to_marp(input_file: Path, format_p: str, output_dir: Path = None, base_name: str = None):
    """
    Public function for converting .marp.file to pdf/pptx file
    """
    if output_dir is None:
        output_dir = input_file.parent
    if base_name is None:
        base_name = input_file.stem.replace('.marp', '')

    pdf_path = output_dir / f"{base_name}.pdf"
    pptx_path = output_dir / f"{base_name}.pptx"

    if format_p in ("pdf", "both"):
        subprocess.run(['marp', input_file, '--pdf', '-o', pdf_path], check=True, stderr=subprocess.DEVNULL)
    if format_p in ("pptx", "both"):
        subprocess.run(['marp', input_file, '--pptx', '-o', pptx_path], check=True, stderr=subprocess.DEVNULL)