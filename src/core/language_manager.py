import os
import json
from typing import List, Dict, Optional, Any
from pathlib import Path


class LanguageManager:
    def __init__(self, languages_dir: str = "languages"):
        self.languages_dir = Path(languages_dir)
        self.current_language = None
        self.numbers = []
        self.available_languages = {}
        
        self._scan_languages()
    
    def _scan_languages(self):
        if not self.languages_dir.exists():
            print(f"Warning: Languages directory '{self.languages_dir}' not found")
            return
        
        for lang_dir in self.languages_dir.iterdir():
            if lang_dir.is_dir():
                lang_code = lang_dir.name
                numbers_file = lang_dir / "numbers.json"
                
                if numbers_file.exists():
                    self.available_languages[lang_code] = {
                        'path': lang_dir,
                        'numbers_file': numbers_file
                    }
                else:
                    print(f"Warning: No numbers.json found in {lang_dir}")
    
    def get_available_languages(self) -> List[str]:
        return list(self.available_languages.keys())
    
    def load_language(self, lang_code: str) -> bool:
        if lang_code not in self.available_languages:
            print(f"Error: Language '{lang_code}' not found")
            return False
        
        try:
            numbers_file = self.available_languages[lang_code]['numbers_file']
            with open(numbers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.numbers = data.get('numbers', [])
            self.current_language = lang_code
            
            if not self.numbers:
                print(f"Warning: No numbers found in {lang_code}")
                return False
            
            print(f"Loaded {len(self.numbers)} numbers for language '{lang_code}'")
            return True
            
        except Exception as e:
            print(f"Error loading language '{lang_code}': {e}")
            return False
    
    def get_current_number(self, index: int) -> Optional[str]:
        if not self.numbers or index < 0 or index >= len(self.numbers):
            return None
        return self.numbers[index]
    
    def get_total_numbers(self) -> int:
        return len(self.numbers)
    
    def get_current_language(self) -> Optional[str]:
        return self.current_language
    
    def validate_language_structure(self, lang_code: str) -> Dict[str, Any]:
        if lang_code not in self.available_languages:
            return {'valid': False, 'error': f'Language {lang_code} not found'}
        
        lang_path = self.available_languages[lang_code]['path']
        numbers_file = lang_path / "numbers.json"
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not numbers_file.exists():
            result['valid'] = False
            result['errors'].append('numbers.json file missing')
            return result
        
        try:
            with open(numbers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'numbers' not in data:
                result['valid'] = False
                result['errors'].append('Missing "numbers" array in JSON')
            elif not isinstance(data['numbers'], list):
                result['valid'] = False
                result['errors'].append('"numbers" must be an array')
            elif len(data['numbers']) == 0:
                result['warnings'].append('No numbers in the array')
            
            if 'metadata' in data:
                metadata = data['metadata']
                if 'language_name' not in metadata:
                    result['warnings'].append('Missing language_name in metadata')
                if 'description' not in metadata:
                    result['warnings'].append('Missing description in metadata')
            
        except json.JSONDecodeError as e:
            result['valid'] = False
            result['errors'].append(f'Invalid JSON: {e}')
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f'Read error: {e}')
        
        return result