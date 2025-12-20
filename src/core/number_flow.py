import sys
import time
from typing import Optional, List, Dict, Any
from .keyboard import KeyboardSimulator
from .language_manager import LanguageManager
from ..styles.jack_styles import StyleManager
from ..config.config_manager import ConfigManager


class NumberFlow:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.keyboard = KeyboardSimulator()
        self.language_manager = LanguageManager()
        self.style_manager = StyleManager()
        
        self.current_index = 0
        self.running = False
        
        self._load_initial_language()
    
    def _load_initial_language(self):
        language = self.config.get_language()
        if not self.language_manager.load_language(language):
            print(f"Failed to load language '{language}'")
            available = self.language_manager.get_available_languages()
            if available:
                print(f"Available languages: {', '.join(available)}")
                if self.language_manager.load_language(available[0]):
                    print(f"Using default language: {available[0]}")
    
    def start(self):
        if not self.language_manager.get_current_language():
            print("No language loaded. Cannot start.")
            return
        
        self.running = True
        self._run_interactive_mode()
    
    def stop(self):
        self.running = False
    
    def _run_interactive_mode(self):
        nav_config = self.config.get_navigation_config()
        type_key = self.config.get_type_key()
        
        print(f"\n=== AutoJJs Number Flow ===")
        print(f"Language: {self.language_manager.get_current_language()}")
        print(f"Style: {self.config.get_jack_style()}")
        print(f"Total numbers: {self.language_manager.get_total_numbers()}")
        print(f"\nControls:")
        print(f"  {nav_config['next']} - Next number")
        print(f"  {nav_config['previous']} - Previous number") 
        print(f"  {nav_config['jump']} - Jump to number")
        print(f"  {nav_config['quit']} - Quit")
        print(f"  {type_key} - Type current number")
        print(f"\n{type_key} to type current number, or use controls...")
        
        try:
            while self.running:
                self._show_current_status()
                
                try:
                    choice = input("\n> ").strip().lower()
                    
                    if choice == nav_config['quit']:
                        break
                    elif choice == nav_config['next']:
                        self._next_number()
                    elif choice == nav_config['previous']:
                        self._previous_number()
                    elif choice == nav_config['jump']:
                        self._jump_to_number()
                    elif choice == self.config.get_type_key():
                        self._type_current_number()
                    else:
                        print("Unknown command")
                        
                except (EOFError, KeyboardInterrupt):
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            print("\nGoodbye!")
    
    def _show_current_status(self):
        current_number = self.language_manager.get_current_number(self.current_index)
        total = self.language_manager.get_total_numbers()
        
        if self.config.should_show_index():
            print(f"\n[{self.current_index + 1}/{total}] ", end="")
        
        if current_number and self.config.should_show_formatted():
            formatted = self._format_number(current_number)
            if len(formatted) == 1:
                print(f"Current: {formatted[0]}")
            else:
                print(f"Current: {' | '.join(formatted[:3])}{'...' if len(formatted) > 3 else ''}")
        
        print(f"Language: {self.language_manager.get_current_language()} | "
              f"Style: {self.config.get_jack_style()}")
    
    def _type_current_number(self):
        current_number = self.language_manager.get_current_number(self.current_index)
        if not current_number:
            print("No number available")
            return
        
        formatted_lines = self._format_number(current_number)
        
        print(f"\nTyping: {current_number}")
        if len(formatted_lines) > 1:
            print(f"Formatted as: {' | '.join(formatted_lines[:3])}{'...' if len(formatted_lines) > 3 else ''}")
        else:
            print(f"Formatted as: {formatted_lines[0]}")
        
        delays = self.config.get_delays()
        typing_config = {
            'prefix_key': self.config.get_prefix_key(),
            'prefix_delay': delays['prefix'],
            'char_delay': delays['character'],
            'enter_delay': delays['enter'],
            'space_delay': delays['space']
        }
        
        for line in formatted_lines:
            self.keyboard.type_sequence(line, typing_config)
            time.sleep(0.1)
        
        self._next_number()
    
    def _format_number(self, number: str) -> List[str]:
        style_name = self.config.get_jack_style()
        style_config = self.config.get_style_config(style_name)
        
        style = self.style_manager.get_style(style_name, style_config)
        return style.format(number)
    
    def _next_number(self):
        total = self.language_manager.get_total_numbers()
        self.current_index = (self.current_index + 1) % total
    
    def _previous_number(self):
        total = self.language_manager.get_total_numbers()
        self.current_index = (self.current_index - 1) % total
    
    def _jump_to_number(self):
        try:
            jump_input = input("Enter number (1-indexed): ").strip()
            if not jump_input:
                return
            
            jump_index = int(jump_input) - 1
            total = self.language_manager.get_total_numbers()
            
            if 0 <= jump_index < total:
                self.current_index = jump_index
                print(f"Jumped to number {jump_index + 1}")
            else:
                print(f"Invalid number. Must be between 1 and {total}")
                
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    def get_current_number(self) -> Optional[str]:
        return self.language_manager.get_current_number(self.current_index)
    
    def set_index(self, index: int):
        total = self.language_manager.get_total_numbers()
        if 0 <= index < total:
            self.current_index = index
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'current_index': self.current_index,
            'total_numbers': self.language_manager.get_total_numbers(),
            'current_language': self.language_manager.get_current_language(),
            'jack_style': self.config.get_jack_style(),
            'running': self.running
        }