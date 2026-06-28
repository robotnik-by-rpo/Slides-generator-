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

        parser.add_argument(
            "--lesson",
            default="undefine",
            help="Numeration lesson"
        )

        args = parser.parse_args()

        if not args.lesson:
            print("Number lesson didn't point in flag --lesson")
            return 1

        if args.update and args.plan:
            print("Many operation in one request")
            return 1

        try:
            self.plan_path = Path(args.plan)
            self.output_dir = self.main_directory / Path(args.output)
            self.lesson = args.lesson

            
            # Проверка существования файла плана
            if not self.plan_path.exists() and not args.update:
                raise FileNotFoundError(f"File .md doesn't exist: {args.plan}")
            
            # Creating output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)        
            parser_md = ParserMD(self.plan_path, self.output_dir, self.marp_theme, self.api_ai)
            parser_md.Parse_file_to_marp()
            self.title = parser_md.title[0]
            convert_to_marp(args.plan, args.format)
            paths_metadata = {"plan": self.next_cloud_url.strip('/')+'/'+self.plan_path.stem}
            
            if args.update:
                return self.process_update_mode(self.output_dir, args.format)

            if args.format == "both":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+'presentation.pdf' 
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+'presentation.pptx'
            elif args.format == "pptx":
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+'presentation.pptx'
            elif args.format == "pdf":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+'presentation.pdf' 

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
            
            save_json_metadata(xAPI, self.output_dir)
            send_lrs(self.lrs_url,xAPI)
            send_next_cloud(xAPI)
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
                
            print(f"Found {len(marp_files)} .marp.md files to update")
            
            for marp_file in marp_files:
                base_name = marp_file.stem.replace('.marp', '')
                print(f"Updating presentation for: {base_name}")
                convert_to_marp(marp_file,format_choice)
            paths_metadata = {"plan": self.next_cloud_url.strip('/')+'/'+self.plan_path.stem}
            if format_choice == "both":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+'presentation.pdf' 
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+'presentation.pptx'
            elif format_choice == "pptx":
                paths_metadata['pptx'] = self.next_cloud_url.strip('/')+'/'+'presentation.pptx'
            elif format_choice == "pdf":
                paths_metadata['pdf'] = self.next_cloud_url.strip('/')+'/'+'presentation.pdf' 

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
            
            save_json_metadata(xAPI, self.output_dir)
            send_lrs(self.lrs_url,xAPI)
            send_next_cloud(xAPI)
            return 0
            
        except Exception as e:
            print(f"Error in update mode: {e}", file=sys.stderr)
            return 1



if __name__ == "__main__":
    cli = CLI()
    sys.exit(cli.main())