import argparse
import sys
from pathlib import Path
import os
from parse.parse import ParserMD
from metadata.metadata import save_json_metadata, send_lrs, send_next_cloud
from generate.generate import convert_to_marp
from datetime import datetime

class CLI:
    def __init__(self):
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
        self.lesson = ""
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
            help="For updating files in all directory"
        )

        parser.add_argument(
            "--lesson",
            default="undefine",
            help="Numeration lesson",
            required=True,
        )

        args = parser.parse_args()

        if args.update and args.plan:
            print("Many operation in one request")
            return 1
        
        if not args.update and not args.plan:
            print("Either --plan or --update must be specified")
            return 1

        if not self.main_directory:
            self.main_directory = Path(".")

        try:
            self.plan_path = Path(args.plan)
            self.output_dir = self.main_directory / Path(args.output)
            self.output_dir.mkdir(parents=True, exist_ok=True)            
            self.lesson = args.lesson

            
            if args.update:
                return self.process_update_mode(self.output_dir, args.format)


            # Проверка существования файла плана
            if not self.plan_path.exists() and not args.update:
                raise FileNotFoundError(f"File .md doesn't exist: {args.plan}")
            
            # Creating output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)        
            parser_md = ParserMD(self.plan_path, self.output_dir, self.marp_theme, self.api_ai)
            path_marp_md = parser_md.Parse_file_to_marp()
            self.title = parser_md.title
            convert_to_marp(path_marp_md, args.format, output_dir=self.output_dir, base_name=self.title)
            paths_metadata = {"plan": self.next_cloud_url.strip('/')+'/'+self.plan_path.name}
            
            if args.format == "both":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pdf' 
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pptx'
            elif args.format == "pptx":
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pptx'
            elif args.format == "pdf":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pdf' 

            xAPI = {
                    "actor": {
                    "mbox": "mailto:teacher@example.com",
                    },
                    "verb": {
                        "id": "http://adlnet.gov/expapi/verbs/generated",
                        "display": {
                            "ru": "Генерация презентации"
                        }
                    },
                    "object": {
                        "id": f"urn:lesson:{self.lesson}",
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
            marp_file = list(directory.glob("*.marp.md"))[0]
            
            if not marp_file:
                print(f"No .marp.md files found in {directory}")
                return 1
                
            
            
            base_name = marp_file.stem.replace('.marp', '')
            self.title = self._extract_title_from_marp()
            print(f"Updating presentation for: {base_name}")
            convert_to_marp(marp_file,format_choice,output_dir=directory,base_name=base_name)
            paths_metadata = {"plan": self.next_cloud_url.strip('/')+'/'+self.plan_path.name}
            if format_choice == "both":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pdf' 
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pptx'
            elif format_choice == "pptx":
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pptx'
            elif format_choice == "pdf":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+f'{self.lesson}.pdf' 

            xAPI = {
                    "actor": {
                    "mbox": "mailto:teacher@example.com",
                    },
                    "verb": {
                        "id": "http://adlnet.gov/expapi/verbs/updated",
                        "display": {
                            "ru": "Обновление презентации"
                        }
                    },
                    "object": {
                        "id": f"urn:lesson:{self.lesson}",
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
                lines = f.readlines()

            in_yaml = False
            content_start = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped == '---':
                    if not in_yaml:
                        in_yaml = True
                    else:
                        content_start = i + 1
                        break

            for line in lines[content_start:]:
                stripped = line.strip()
                if stripped.startswith('# '):
                    return stripped[2:].strip()
                if stripped.startswith('## '):
                    return stripped[3:].strip()
            return marp_file.stem.replace('.marp', '')

        except Exception as e:
            print(f"Warning: Could not extract title from {marp_file}: {e}")
            return marp_file.stem.replace('.marp', '')


if __name__ == "__main__":
    cli = CLI()
    sys.exit(cli.main())