import time
import threading
from typing import Optional, Dict, Any

try:
    import uinput
    UINPUT_AVAILABLE = True
except ImportError:
    uinput = None
    UINPUT_AVAILABLE = False

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    keyboard = None
    PYNPUT_AVAILABLE = False


class KeyboardSimulator:
    def __init__(self):
        self.device = None
        self._lock = threading.Lock()
        
        if not UINPUT_AVAILABLE:
            print("Warning: python-uinput not available. Running in debug mode.")
            return
        
        self._initialize_device()
    
    def _initialize_device(self):
        try:
            self.device = uinput.Device([
                uinput.KEY_ENTER,
                uinput.KEY_SPACE,
                uinput.KEY_SLASH,
                uinput.KEY_BACKSPACE,
                uinput.KEY_LEFT,
                uinput.KEY_RIGHT,
                uinput.KEY_UP,
                uinput.KEY_DOWN,
                uinput.KEY_ESC,
                uinput.KEY_LEFTSHIFT,
                *self._get_all_char_keys()
            ])
        except PermissionError:
            raise PermissionError(
                "Failed to create uinput device. "
                "Make sure you have proper permissions and the uinput module is loaded. "
                "Try: sudo modprobe uinput && sudo usermod -a -G input $USER"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize keyboard: {e}")
    
    def _get_all_char_keys(self):
        char_keys = []
        
        key_names = [
            'KEY_A', 'KEY_B', 'KEY_C', 'KEY_D', 'KEY_E', 'KEY_F', 'KEY_G', 
            'KEY_H', 'KEY_I', 'KEY_J', 'KEY_K', 'KEY_L', 'KEY_M', 'KEY_N', 
            'KEY_O', 'KEY_P', 'KEY_Q', 'KEY_R', 'KEY_S', 'KEY_T', 'KEY_U', 
            'KEY_V', 'KEY_W', 'KEY_X', 'KEY_Y', 'KEY_Z',
            'KEY_0', 'KEY_1', 'KEY_2', 'KEY_3', 'KEY_4', 'KEY_5', 'KEY_6', 
            'KEY_7', 'KEY_8', 'KEY_9',
            'KEY_MINUS', 'KEY_EQUAL', 'KEY_LEFTBRACE', 'KEY_RIGHTBRACE',
            'KEY_SEMICOLON', 'KEY_APOSTROPHE', 'KEY_GRAVE', 'KEY_BACKSLASH',
            'KEY_COMMA', 'KEY_DOT'
        ]
        
        for key_name in key_names:
            if hasattr(uinput, key_name):
                char_keys.append(getattr(uinput, key_name))
        
        return char_keys
    
    def _get_key_for_char(self, char: str) -> Optional[int]:
        char = char.upper()
        
        key_map = {
            'A': 'KEY_A', 'B': 'KEY_B', 'C': 'KEY_C', 'D': 'KEY_D',
            'E': 'KEY_E', 'F': 'KEY_F', 'G': 'KEY_G', 'H': 'KEY_H',
            'I': 'KEY_I', 'J': 'KEY_J', 'K': 'KEY_K', 'L': 'KEY_L',
            'M': 'KEY_M', 'N': 'KEY_N', 'O': 'KEY_O', 'P': 'KEY_P',
            'Q': 'KEY_Q', 'R': 'KEY_R', 'S': 'KEY_S', 'T': 'KEY_T',
            'U': 'KEY_U', 'V': 'KEY_V', 'W': 'KEY_W', 'X': 'KEY_X',
            'Y': 'KEY_Y', 'Z': 'KEY_Z',
            '0': 'KEY_0', '1': 'KEY_1', '2': 'KEY_2', '3': 'KEY_3',
            '4': 'KEY_4', '5': 'KEY_5', '6': 'KEY_6', '7': 'KEY_7',
            '8': 'KEY_8', '9': 'KEY_9',
            '-': 'KEY_MINUS', '=': 'KEY_EQUAL', '[': 'KEY_LEFTBRACE',
            ']': 'KEY_RIGHTBRACE', ';': 'KEY_SEMICOLON', "'": 'KEY_APOSTROPHE',
            '`': 'KEY_GRAVE', '\\': 'KEY_BACKSLASH', ',': 'KEY_COMMA',
            '.': 'KEY_DOT', '!': 'KEY_1', '?': 'KEY_SLASH'
        }
        
        key_name = key_map.get(char)
        if key_name and hasattr(uinput, key_name):
            return getattr(uinput, key_name)
        
        return None
    
    def type_text(self, text: str, char_delay: float = 0.05):
        if not UINPUT_AVAILABLE or self.device is None:
            print(f"DEBUG: Would type: {text}")
            return
            
        with self._lock:
            for char in text:
                if char == ' ':
                    self.device.emit(uinput.KEY_SPACE, 1)
                    self.device.emit(uinput.KEY_SPACE, 0)
                else:
                    key = self._get_key_for_char(char)
                    if key:
                        shift_needed = char.isupper() and char.isalpha()
                        
                        # Special handling for ! and ?
                        if char == '!':
                            shift_needed = True
                        elif char == '?':
                            shift_needed = True
                        
                        if shift_needed:
                            self.device.emit(uinput.KEY_LEFTSHIFT, 1)
                        
                        self.device.emit(key, 1)
                        self.device.emit(key, 0)
                        
                        if shift_needed:
                            self.device.emit(uinput.KEY_LEFTSHIFT, 0)
                        else:
                            print(f"Warning: Cannot type character '{char}'")
                
                time.sleep(char_delay)
    
    def press_key(self, key: int, delay: float = 0.1):
        if not UINPUT_AVAILABLE or self.device is None:
            print(f"DEBUG: Would press key: {key}")
            return
            
        with self._lock:
            self.device.emit(key, 1)
            self.device.emit(key, 0)
            time.sleep(delay)
    
    def press_enter(self, delay: float = 0.2):
        if UINPUT_AVAILABLE and self.device is not None:
            self.press_key(uinput.KEY_ENTER, delay)
        else:
            print("DEBUG: Would press Enter")
    
    def press_space(self, delay: float = 0.2):
        if UINPUT_AVAILABLE and self.device is not None:
            self.press_key(uinput.KEY_SPACE, delay)
        else:
            print("DEBUG: Would press Space")
    
    def press_prefix(self, prefix_key: str = '/', delay: float = 0.1):
        if prefix_key == '/':
            if UINPUT_AVAILABLE and self.device is not None:
                self.press_key(uinput.KEY_SLASH, delay)
            else:
                print("DEBUG: Would press /")
        else:
            key = self._get_key_for_char(prefix_key)
            if key:
                self.press_key(key, delay)
    
    def type_sequence(self, text: str, config: Dict[str, Any], auto_jumping: bool = False):
        prefix_delay = config.get('prefix_delay', 0.1)
        char_delay = config.get('char_delay', 0.05)
        enter_delay = config.get('enter_delay', 0.2)
        space_delay = config.get('space_delay', 0.2)
        prefix_key = config.get('prefix_key', '/')
        
        if auto_jumping:
            self.press_space(0.2)  # Press space
            time.sleep(0.2)         # Wait 200ms
        
        self.press_prefix(prefix_key, prefix_delay)
        
        self.type_text(text, char_delay)
        self.press_enter(enter_delay)