import subprocess
from pathlib import Path
import re

def sanitize_filename(name: str) -> str:
    """
    Delete spaces in name of lesson

    Args:
        name: name of file

    """
    safe = re.sub(r'[^a-zA-Zа-яА-Я0-9_\-\s]', '_', name)
    safe = re.sub(r'\s+', '_', safe)
    safe = re.sub(r'_+', '_', safe)
    safe = safe.strip('_')
    return safe if safe else 'presentation'

def convert_to_marp(input_file: Path, format_p: str, output_dir: Path = None, base_name: str = None):
    """
    Public function for converting .marp.file to pdf/pptx file
    """
    if output_dir is None:
        output_dir = input_file.parent
    if base_name is None:
        base_name = input_file.stem.replace('.marp', '')
    else:
        base_name = sanitize_filename(base_name)

    pdf_path = output_dir / f"{base_name}.pdf"
    pptx_path = output_dir / f"{base_name}.pptx"
    html_path = output_dir / f"{base_name}.html"

    if format_p in ("pdf", "all"):
        subprocess.run(['marp', input_file, '--pdf', '-o', pdf_path], check=True, stderr=subprocess.DEVNULL)
    if format_p in ("pptx", "all"):
        subprocess.run(['marp', input_file, '--pptx', '-o', pptx_path], check=True, stderr=subprocess.DEVNULL)
    if format_p in ("html","all"):
        subprocess.run(['marp', input_file, '--html', '-o', html_path], check=True, stderr=subprocess.DEVNULL)
