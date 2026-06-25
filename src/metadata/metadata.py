import json
from typing import Generator, Optional
from pathlib import Path

def Save_json_metadata(data: dict, path: Path):
    """Public function for saving metadata to json file"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)