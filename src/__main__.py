import argparse
import sys
from pathlib import Path
import os
from parse.parse import ParserMD
from metadata.metadata import Save_json_metadata
from generate.generate import convert_to_marp
import requests

def main()->int:
    main_directory = Path(os.environ.get('SLIDES_OUTPUT_FOLDER'))
    lrs_url = os.environ.get('LRS_ENDPOINT')
    marp_theme = os.environ.get('THEME_MARP', "default")
    api_ai = os.environ.get('API_AI')
    statement = "generated"
    xAPI = {}

    # In future
    api_marp = os.environ.get('API_KEY_MARP')

    parser = argparse.ArgumentParser(
        description="Slider-generator"
    )

    parser.add_argument(
        "--plan",
        required=True,
        help = "Path to file of lesson",
    )

    parser.add_argument(
        "--output",
        default="./output",
        help="Directory for saving presentation"
    )

    parser.add_argument(
        "--format",
        choices=["pdf", "pptx", "both"],
        default="both",
        help="This is format output data"
    )
    
    parser.add_argument(
        "--update",
        help="For updating files in all directory"
    )

    args = parser.parse_args()
    try:
        plan_path = Path(args.plan)
        output_dir = main_directory / Path(args.output)

        if args.update:
            statement = "Updated"
            return process_update_mode(output_dir, args.format)

        # Проверка существования файла плана
        if not plan_path.exists():
            raise FileNotFoundError(f"File .md doesn't exist: {args.plan}")
        
        # Creating output directory
        output_dir.mkdir(parents=True, exist_ok=True)        
        parser_md = ParserMD(plan_path, output_dir, marp_theme,api_ai)
        parser_md.Parse_file_to_marp()
        convert_to_marp(args.plan, args.format)
        return 0
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

def process_update_mode(directory: Path, format_choice: str)->int:
    """
    Process update mode: find all .marp.md files and regenerate presentations
    """
    try:
        marp_files = list(directory.glob("*.marp.md"))
        
        if not marp_files:
            print(f"No .marp.md files found in {directory}")
            return 1
            
        print(f"Found {len(marp_files)} .marp.md files to update")
        
        for marp_file in marp_files:
            base_name = marp_file.stem.replace('.marp', '')
            print(f"Updating presentation for: {base_name}")
            convert_to_marp(marp_file,format_choice)
        return 0
        
    except Exception as e:
        print(f"Error in update mode: {e}", file=sys.stderr)
        return 1



if __name__ == "__main__":
    sys.exit(main())