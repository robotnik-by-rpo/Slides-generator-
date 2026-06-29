import argparse
import sys
from pathlib import Path
import os
import json
from parse.parse import ParserMD
from metadata.metadata import save_json_metadata, send_lrs, send_next_cloud
from generate.generate import convert_to_marp, sanitize_filename
from datetime import datetime

class CLI:
    def __init__(self):
        try:
            self.main_directory = Path(os.environ.get('SLIDES_OUTPUT_FOLDER'))
            self.lrs_url = os.environ.get('LRS_ENDPOINT')
            self.marp_theme = os.environ.get('THEME_MARP', "default")
            self.api_ai = os.environ.get('API_AI')
            self.login_lrs = os.environ.get("LOGIN_LRS")
            self.next_cloud_url = os.environ.get("API_NEXTCLOUD")
            self.api_marp = os.environ.get('API_KEY_MARP') # In future
            self.plan_path = ""
            self.output_dir = ""
            self.title = ""
        except Exception as e:
            print("Empty token in .env", e)
    def main(self)->int:
    
        parser = argparse.ArgumentParser(
            description="Slider-generator"
        )

        parser.add_argument(
            "--plan",
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
            metavar="DIR",
            help="Update presentations in specified directory (must contain .marp.md files)"
        )


        args = parser.parse_args()

        if args.update and args.plan:
            print("Error: --update and --plan cannot be used together")
            return 1
        
        if not args.update and not args.plan:
            print("Either --plan or --update must be specified")
            return 1

        if not self.main_directory:
            self.main_directory = Path(".")

        try:

                        
            if args.update:
                return self.process_update_mode(Path(args.update), args.format)


            self.plan_path = Path(args.plan)
            self.output_dir = self.main_directory / Path(args.output)
            self.output_dir.mkdir(parents=True, exist_ok=True)            

            if not self.plan_path.exists() and not args.update:
                raise FileNotFoundError(f"File .md doesn't exist: {args.plan}")
            
            # Creating output directory
            parser_md = ParserMD(self.plan_path, self.output_dir, self.marp_theme, self.api_ai)
            path_marp_md = parser_md.Parse_file_to_marp()
            self.title = parser_md.title

            safe_title = sanitize_filename(self.title)
            convert_to_marp(path_marp_md, args.format, output_dir=self.output_dir, base_name=self.title)
            paths_metadata = {"plan": self.next_cloud_url.strip('/')+'/'+self.plan_path.name}
            
            if args.format in ("pdf", "both"):
                paths_metadata['pdf'] = self.next_cloud_url.strip('/') + '/' + f'{safe_title}.pdf'
            if args.format in ("pptx", "both"):
                paths_metadata['pptx'] = self.next_cloud_url.strip('/') + '/' + f'{safe_title}.pptx'

            xAPI = {
                    "actor": {
                    "mbox": self.login_lrs,
                    },
                    "verb": {
                        "id": "http://adlnet.gov/expapi/verbs/generated",
                        "display": {
                            "ru": "Генерация презентации"
                        }
                    },
                    "object": {
                        "id": f"urn:lesson:{self.title}",
                        "definition": {
                            "name": {
                                "ru": self.title,
                            }
                        }
                    },
                    "context": {
                        "extensions": {
                            "plan_url": paths_metadata["plan"],
                            "slides_url_pdf": paths_metadata.get("pdf",""),
                            "slides_url_pptx": paths_metadata.get("pptx",""),
                        }
                    },
                    "timestamp": datetime.now().isoformat(timespec='seconds')
                }
            
            paths_metadata["metadata"] = xAPI
            save_json_metadata(xAPI, self.output_dir / "metadata.json")
            send_lrs(self.lrs_url,xAPI)
            send_next_cloud(paths_metadata)
            return 0
        except Exception as e:
            print(e, file=sys.stderr)
            return 1

    def process_update_mode(self,directory: Path, format_choice: str)->int:
        """
        Process update mode: find all .marp.md files and regenerate presentations

        Args:
            directory: path for saving directory
            format_choice: format to saving
        """
        try:
            marp_files = list(directory.glob("*.marp.md"))
            
            if not marp_files:
                print(f"No .marp.md files found in {directory}")
                return 1
                
            if len(marp_files) > 1:
                print(f"Warning: Multiple .marp.md files found. Using the first one: {marp_files[0].name}")

            marp_file = marp_files[0]
            base_name = marp_file.stem.replace('.marp', '')
            self.title = self._extract_title_from_marp(marp_file)
            print(f"Updating presentation for: {base_name}")
            safe_base = sanitize_filename(base_name)
            convert_to_marp(marp_file,format_choice,output_dir=directory,base_name=safe_base)
            paths_metadata = {"plan": self._get_plan_from_metadata(self.output_dir / "metadata.json")}
            if format_choice in ("pdf", "both"):
                paths_metadata['pdf'] = self.next_cloud_url.strip('/') + '/' + f'{safe_base}.pdf'
            if format_choice in ("pptx", "both"):
                paths_metadata['pptx'] = self.next_cloud_url.strip('/') + '/' + f'{safe_base}.pptx' 

            xAPI = {
                    "actor": {
                    "mbox": self.login_lrs,
                    },
                    "verb": {
                        "id": "http://adlnet.gov/expapi/verbs/updated",
                        "display": {
                            "ru": "Обновление презентации"
                        }
                    },
                    "object": {
                        "id": f"urn:lesson:{self.title}",
                        "definition": {
                            "name": {
                                "ru": self.title,
                            }
                        }
                    },
                    "context": {
                        "extensions": {
                            "plan_url": paths_metadata["plan"],
                            "slides_url_pdf": paths_metadata.get("pdf",""),
                            "slides_url_pptx": paths_metadata.get("pptx",""),
                        }
                    },
                    "timestamp": datetime.now().isoformat(timespec='seconds')
                }
            
            paths_metadata["metadata"] = xAPI
            save_json_metadata(xAPI, self.output_dir / "metadata.json")
            send_lrs(self.lrs_url,xAPI)
            send_next_cloud(paths_metadata)
            return 0
            
        except Exception as e:
            print(f"Error in update mode: {e}", file=sys.stderr)
            return 1
        
    def _extract_title_from_marp(self, marp_file: Path) -> str:
        """
        Extracting title from marp-file was generated 

        Args:
            marp_file: path to file .marp.md

        Returns:
            string with title or file name without .marp.md, if title didn't found
        """
        try:
            with open(marp_file, 'r', encoding='utf-8') as f:
                in_yaml = False
                for line in f:
                    stripped = line.strip()
                    if stripped == '---':
                        in_yaml = not in_yaml
                        continue
                    if in_yaml:
                        continue
                    if stripped.startswith('# '):
                        return stripped[2:].strip()
                    if stripped.startswith('## '):
                        return stripped[3:].strip()
            return marp_file.stem.replace('.marp', '')
        except Exception as e:
            return marp_file.stem.replace('.marp', '')

    def _get_plan_from_metadata(self, file_path: str)->str:
        """
        Public method for getting plan from metadata
        Args:
            file_path: path to file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data["context"]["extensions"]["plan_url"]
        except Exception as e:
            print("Json metadata doesn't exist in this directory",e)
            return ""

if __name__ == "__main__":
    cli = CLI()
    sys.exit(cli.main())