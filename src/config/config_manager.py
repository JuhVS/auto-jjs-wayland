import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    DEFAULT_CONFIG = {
        "language": "en",
        "prefix_key": "/",
        "jack_style": "JJs",
        "delays": {
            "prefix": 0.1,
            "character": 0.05,
            "enter": 0.2,
            "space": 0.2
        },
        "navigation": {
            "next": "n",
            "previous": "p",
            "jump": "j",
            "quit": "q",
            "type": "."
        },
        "styles": {
            "JJs": {
                "ending": ".",
                "case": "capitalize"
            },
            "HJs": {
                "ending": "!",
                "case": "normal"
            },
            "GJs": {
                "ending": ".",
                "case": "normal"
            }
        },
        "debug": {
            "show_index": True,
            "show_formatted": True,
            "verbose": False
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self._merge_config(self.config, user_config)
                print(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
        else:
            print(f"Config file {self.config_file} not found, creating default")
            self.save_config()
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]):
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_language(self) -> str:
        return self.get('language', 'en')
    
    def set_language(self, language: str):
        self.set('language', language)
    
    def get_prefix_key(self) -> str:
        return self.get('prefix_key', '/')
    
    def set_prefix_key(self, key: str):
        self.set('prefix_key', key)
    
    def get_jack_style(self) -> str:
        return self.get('jack_style', 'JJs')
    
    def set_jack_style(self, style: str):
        self.set('jack_style', style)
    
    def get_delays(self) -> Dict[str, float]:
        return self.get('delays', self.DEFAULT_CONFIG['delays'])
    
    def get_style_config(self, style_name: str) -> Dict[str, Any]:
        return self.get(f'styles.{style_name}', {})
    
    def get_navigation_config(self) -> Dict[str, str]:
        return self.get('navigation', self.DEFAULT_CONFIG['navigation'])
    
    def get_type_key(self) -> str:
        return self.get('navigation.type', '.')
    
    def is_debug_enabled(self) -> bool:
        return self.get('debug.verbose', False)
    
    def should_show_index(self) -> bool:
        return self.get('debug.show_index', True)
    
    def should_show_formatted(self) -> bool:
        return self.get('debug.show_formatted', True)
    
    def validate_config(self) -> Dict[str, Any]:
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        delays = self.get_delays()
        for delay_name, delay_value in delays.items():
            if not isinstance(delay_value, (int, float)) or delay_value < 0:
                result['errors'].append(f'Invalid delay value for {delay_name}: {delay_value}')
        
        style = self.get_jack_style()
        if style not in ['JJs', 'HJs', 'GJs']:
            result['warnings'].append(f'Unknown jack style: {style}')
        
        prefix_key = self.get_prefix_key()
        if len(prefix_key) != 1:
            result['errors'].append('Prefix key must be a single character')
        
        return result