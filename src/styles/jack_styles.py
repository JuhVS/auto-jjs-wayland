from abc import ABC, abstractmethod
from typing import List, Dict, Any


class JackStyle(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def format(self, text: str) -> List[str]:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass


class JJsStyle(JackStyle):
    def get_name(self) -> str:
        return "JJs"
    
    def format(self, text: str) -> List[str]:
        ending = self.config.get('ending', '.')
        case_rule = self.config.get('case', 'capitalize')
        
        if case_rule == 'upper':
            formatted = text.upper()
        elif case_rule == 'lower':
            formatted = text.lower()
        else:  # capitalize - capitalize each word
            formatted = ' '.join(word.capitalize() for word in text.split())
        
        return [formatted + ending]


class HJsStyle(JackStyle):
    def get_name(self) -> str:
        return "HJs"
    
    def format(self, text: str) -> List[str]:
        ending = self.config.get('ending', '!')
        case_rule = self.config.get('case', 'normal')
        add_full_number = self.config.get('add_full_number', True)
        uppercase = case_rule == 'upper'
        
        result = []
        
        # Process each character
        for char in text:
            if char == '-':
                continue
            elif char == ' ':
                continue
            else:
                if uppercase:
                    result.append(char.upper() + ending)
                else:
                    result.append(char.upper() + ending)
        
        # Add full number at the end if enabled
        if add_full_number:
            full_number = text.upper().replace('-', '').replace(' ', '')
            result.append(full_number + '!')
        
        return result


class GJsStyle(JackStyle):
    def get_name(self) -> str:
        return "GJs"
    
    def format(self, text: str) -> List[str]:
        ending = self.config.get('ending', '.')
        case_rule = self.config.get('case', 'capitalize')
        
        if case_rule == 'upper':
            formatted = text.upper()
        elif case_rule == 'lower':
            formatted = text.lower()
        elif case_rule == 'capitalize':
            formatted = ' '.join(word.capitalize() for word in text.split())
        else:  # normal
            formatted = text
        
        return [formatted + ending]


class StyleManager:
    def __init__(self):
        self.styles = {
            'JJs': JJsStyle,
            'HJs': HJsStyle,
            'GJs': GJsStyle
        }
    
    def get_style(self, style_name: str, config: Dict[str, Any]) -> JackStyle:
        if style_name not in self.styles:
            raise ValueError(f"Unknown style: {style_name}")
        
        return self.styles[style_name](config)
    
    def get_available_styles(self) -> List[str]:
        return list(self.styles.keys())
    
    def register_style(self, name: str, style_class: type):
        if not issubclass(style_class, JackStyle):
            raise ValueError("Style class must inherit from JackStyle")
        
        self.styles[name] = style_class