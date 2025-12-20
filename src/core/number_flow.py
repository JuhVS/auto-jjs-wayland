import sys
import time
import random
import threading
from typing import Optional, List, Dict, Any
from .keyboard import KeyboardSimulator
from .language_manager import LanguageManager
from ..styles.jack_styles import StyleManager
from ..config.config_manager import ConfigManager

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    keyboard = None
    PYNPUT_AVAILABLE = False


class NumberFlow:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.keyboard = KeyboardSimulator()
        self.language_manager = LanguageManager()
        self.style_manager = StyleManager()
        
        self.current_index = 0
        self.running = False
        self.last_key_time = 0
        self.key_debounce = 0.2  # 200ms debounce to prevent rapid firing
        self.auto_thread = None
        
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
        if PYNPUT_AVAILABLE:
            self._run_global_mode()
        else:
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
    
    def _run_global_mode(self):
        nav_config = self.config.get_navigation_config()
        type_key = self.config.get_type_key()
        auto_mode = self.config.is_automatic_mode()
        
        print(f"\n=== AutoJJs Number Flow ===")
        print(f"Language: {self.language_manager.get_current_language()}")
        print(f"Style: {self.config.get_jack_style()}")
        print(f"Total numbers: {self.language_manager.get_total_numbers()}")
        print(f"Auto Mode: {'Enabled' if auto_mode else 'Disabled'}")
        print(f"\nGlobal Controls (press anywhere):")
        print(f"  {nav_config['next']} - Next number")
        print(f"  {nav_config['previous']} - Previous number") 
        print(f"  {nav_config['jump']} - Jump to number")
        print(f"  {nav_config['quit']} - Quit")
        print(f"  {type_key} - Type current number {'(auto mode)' if auto_mode else ''}")
        
        special_keys = self.config.get('navigation.special_keys', {})
        type_special = special_keys.get('type')
        if type_special:
            print(f"  {type_special} - Type current number {'(auto mode)' if auto_mode else ''}")
        print(f"\nPress ESC, Ctrl+C or {nav_config['quit']} to stop...")
        
        def on_press(key):
            current_time = time.time()
            
            # Debounce: prevent rapid key repeat
            if current_time - self.last_key_time < self.key_debounce:
                return
                
            try:
                # Debug level 2: show key detection
                if self.config.should_show_keys():
                    try:
                        if hasattr(key, 'char') and key.char:
                            print(f"[DEBUG2] Key pressed: {key.char}")
                        else:
                            print(f"[DEBUG2] Special key: {key}")
                    except:
                        print(f"[DEBUG2] Unknown key type: {type(key)}")
                
                # Handle regular character keys
                if hasattr(key, 'char') and key.char:
                    char = key.char.lower()
                    
                    if char == nav_config['quit']:
                        print("\nQuit key pressed - stopping...")
                        self.stop()
                        return False
                    elif char == nav_config['next']:
                        self._next_number()
                        self._show_current_status()
                        self.last_key_time = current_time
                    elif char == nav_config['previous']:
                        self._previous_number()
                        self._show_current_status()
                        self.last_key_time = current_time
                    elif char == nav_config['jump']:
                        self._jump_to_number_global()
                        self.last_key_time = current_time
                    elif char == type_key:
                        if auto_mode:
                            self._start_automatic_typing()
                        else:
                            self._type_current_number()
                        self.last_key_time = current_time
                # Handle special keys like ESC
                else:
                    if keyboard and hasattr(keyboard, 'Key'):
                        if key == keyboard.Key.esc:
                            print("\nESC pressed - stopping...")
                            self.stop()
                            return False
                        # Handle configurable special keys
                        elif hasattr(key, 'name') and key.name:
                            special_keys = self.config.get('navigation.special_keys', {})
                            type_special = special_keys.get('type')
                            if type_special and key.name == type_special:
                                if auto_mode:
                                    self._start_automatic_typing()
                                else:
                                    self._type_current_number()
                                self.last_key_time = current_time
                        
            except Exception as e:
                if self.config.is_debug_level(1):
                    print(f"Error handling key: {e}")
        
        self._show_current_status()
        
        if PYNPUT_AVAILABLE and keyboard:
            # Create and start listener like in your example
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nInterrupted by user")
            finally:
                self.stop()
                if listener.is_alive():
                    listener.stop()
        else:
            print("pynput not available, falling back to terminal mode")
            self._run_interactive_mode()
    
    def _start_automatic_typing(self):
        if self.auto_thread and self.auto_thread.is_alive():
            print("Automatic typing already running...")
            return
        
        min_delay, max_delay = self.config.get_automatic_delays()
        random_delay = random.uniform(min_delay, max_delay)
        
        print(f"Starting automatic typing in {random_delay:.1f} seconds...")
        
        def auto_type():
            time.sleep(random_delay)
            while self.running:
                self._type_current_number()
                # Random delay between each number
                delay = random.uniform(min_delay, max_delay)
                if self.config.is_debug_level(1):
                    print(f"[DEBUG1] Next automatic type in {delay:.1f}s")
                time.sleep(delay)
        
        self.auto_thread = threading.Thread(target=auto_type, daemon=True)
        self.auto_thread.start()
    
    def _jump_to_number_global(self):
        print("\nJump to number (1-indexed): ", end="", flush=True)
        try:
            # Temporarily switch to terminal input for jump
            jump_input = input()
            if not jump_input:
                return
            
            jump_index = int(jump_input) - 1
            total = self.language_manager.get_total_numbers()
            
            if 0 <= jump_index < total:
                self.current_index = jump_index
                print(f"Jumped to number {jump_index + 1}")
                self._show_current_status()
            else:
                print(f"Invalid number. Must be between 1 and {total}")
                self._show_current_status()
                
        except ValueError:
            print("Invalid input. Please enter a number.")
            self._show_current_status()
        except (EOFError, KeyboardInterrupt):
            pass
    
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