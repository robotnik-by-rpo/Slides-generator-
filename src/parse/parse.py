from pathlib import Path
from typing import Generator, Optional, Dict, Any
import yaml
import requests


class ParserMD:
    """
    Class for processing Markdown files and generating presentations via Groq API.
    """
    
    def __init__(self, path_lesson: Path, path_presentation: Path, theme: str, api: str):
        """
        Initialize the parser.
        
        Args:
            path_lesson: Path to the source .md file with lesson plan
            path_presentation: Directory for saving the presentation
            theme: Marp theme for styling
            api: Groq API key
        """
        self.path_lesson = path_lesson
        self.path_presentation = path_presentation
        self.theme_marp = theme
        self.title = ""
        self.api_key = api
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, str]:
        """
        Protected method for loading prompts from YAML file.
        
        Returns:
            Dictionary containing system prompt and user template
            
        Raises:
            FileNotFoundError: If prompts file doesn't exist
        """
        prompts_path = Path(__file__).parent.parent.parent / 'prompts' / 'generate_presentation.yaml'
        
        if not prompts_path.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_path}")
        
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts_data = yaml.safe_load(f)
        
        return {
            'system': prompts_data.get('system_prompt', ''),
            'user_template': prompts_data.get('user_prompt_template', '')
        }
    
    def parse_file_to_marp(self) -> Optional[Path]:
        """
        Public main method for generating presentation.
        
        Returns:
            Path to the created .marp.md file or None if error occurs
        """
        try:
            plan_content = self._read_plan_file()
            self.title = self._extract_title(plan_content)
            
            marp_content = self._generate_presentation_with_ai(plan_content)
            marp_file_path = self._save_marp_file(marp_content)
            
            return marp_file_path
            
        except Exception as e:
            print(f"Error generating presentation: {e}")
            return None
    
    def _read_plan_file(self) -> str:
        """
        Protected method for reading the contents of the plan file.
        
        Returns:
            File contents as a string
        """
        with open(self.path_lesson, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_title(self, content: str) -> str:
        """
        Protected method for extractng title from plan content.
        
        Args:
            content: Plan content as string
            
        Returns:
            Extracted title or default if not found
        """
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()
            elif line.strip().startswith('## '):
                return line.strip()[3:].strip()
        return "Presentation"
    
    def _generate_presentation_with_ai(self, plan_content: str) -> str:
        """
        Protected method for generating presentation via Groq API.
        
        Args:
            plan_content: Lesson plan content
            
        Returns:
            Generated Marp Markdown
            
        Raises:
            ValueError: If API key is not provided
            requests.exceptions.RequestException: If API request fails
        """
        if not self.api_key:
            raise ValueError("API key is required for generating presentation")
        
        system_prompt = self.prompts['system']
        user_prompt = self.prompts['user_template'].format(
            plan_content=plan_content,
            title=self.title,
            theme=self.theme_marp
        )
        
        # Build Groq API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 5000,
            "top_p": 1
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            marp_content = result['choices'][0]['message']['content']            
            marp_content = self._add_metadata(marp_content)
            
            return marp_content
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Groq API: {e}")
            raise
    
    def _add_metadata(self, content: str) -> str:
        """
        Protected method for adding metadata to the generated presentation.
        
        Args:
            content: Presentation content
            
        Returns:
            Content with metadata added
        """
        metadata = f"""---
marp: true
theme: {self.theme_marp}
size: 16:9
paginate: true
---
"""
        # Check if metadata already exists
        if not content.startswith('---'):
            return metadata + content
        else:
            lines = content.split('\n')
            end_meta = 0
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    end_meta = i + 1
                    break
            
            if end_meta > 0:
                new_content = '\n'.join(lines[end_meta:])
                return metadata + new_content
            else:
                return content
    
    def _save_marp_file(self, content: str) -> Path:
        """
        Protected methods for saving the generated Marp Markdown to a file.
        
        Args:
            content: Marp Markdown content
            
        Returns:
            Path to the saved file
        """
        marp_file_path = self.path_presentation / f"{self.path_lesson.stem}.marp.md"
        
        with open(marp_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return marp_file_path
