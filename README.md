# Mei's AutoJJs - Fully Customizable Auto-typing Jacks System (EN / PT-BR)

[BETA] A Python system for Linux Wayland that uses the **uinput kernel module** to simulate keyboard input for typing numbers written in text form across unlimited languages.

## Features

- **Modular Architecture**: Clean, extensible design with separate components for keyboard input, language management, styling, and configuration
- **Unlimited Languages**: Add new languages by simply creating folders with JSON files - no code changes needed
- **Multiple Jack Styles**: JJs (sentence), HJs (letter-by-letter), and GJs (normal) with configurable formatting
- **Wayland Compatible**: Uses python-uinput for kernel-level keyboard simulation
- **Global Key Detection**: Uses pynput for system-wide key detection (works across all applications)
- **Automatic Mode**: Configurable auto-typing with random delays
- **Interactive Navigation**: Full control over number flow with next/previous/jump commands
- **Configuration Driven**: All settings configurable via JSON file
- **Debug Levels**: Multiple debug levels for troubleshooting

## Quick Start

### Prerequisites

1. **Linux with Wayland**
2. **Python 3.7+**
3. **uinput kernel module**:
   ```bash
   sudo modprobe uinput
   sudo usermod -a -G input $USER
   # Logout and login again
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AutoJJs
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note**: If pynput installation fails on your system, you may need to:
   ```bash
   # Option 1: System package manager (not tested)
   pacman -S python-pynput
   
   # Option 2: Override protection (not recommended)
   pip install pynput --break-system-packages
   
   # Option 3: Virtual environment (recommended and tested)
   python -m venv venv && source venv/bin/activate && pip install pynput
   ```

3. Make the main script executable:
   ```bash
   chmod +x main.py
   ```

### Basic Usage

Start with default settings (English language, JJs style):
```bash
./main.py
```

Use different language or style:
```bash
./main.py -l ptbr -s HJs
```

Enable debug mode:
```bash
./main.py --debug 1          # Basic debug
./main.py --debug 2          # Detailed debug with key detection
```

List available languages:
```bash
./main.py --list-languages
```

Validate system configuration:
```bash
./main.py --validate
```

## Project Structure

```
AutoJJs/
├── main.py                 # Main entry point
├── config.json            # Configuration file (auto-created)
├── requirements.txt       # Python dependencies
├── src/
│   ├── core/
│   │   ├── keyboard.py       # uinput keyboard simulation
│   │   ├── language_manager.py # Dynamic language loading
│   │   └── number_flow.py     # Main flow control
│   ├── styles/
│   │   └── jack_styles.py    # JJs, HJs, GJs style implementations
│   └── config/
│       └── config_manager.py  # Configuration management
└── languages/               # Language folders
    ├── en/
    │   └── numbers.json     # English numbers
    ├── ptbr/
    │   └── numbers.json     # Portuguese Brazilian numbers
    └── [your_language]/     # Add new languages here
        └── numbers.json
```

## Adding New Languages

1. Create a new folder in `languages/` (e.g., `languages/fr`)
2. Add a `numbers.json` file with the following structure:

```json
{
  "metadata": {
    "language_name": "Français",
    "description": "Nombres en français",
    "version": "1.0",
    "author": "Your Name"
  },
  "numbers": [
    "zéro",
    "un",
    "deux",
    "trois",
    ...
  ]
}
```

3. The language is automatically detected and available:
   ```bash
   ./main.py --list-languages
   ./main.py -l fr
   ```

## Jack Styles

### JJs (Jack Sentences)
- Sentence-style output
- Capitalized first letter
- Configurable ending (., !, or none)

**Example**: `One hundred twenty-two.`

### HJs (Hell Jacks)
- Letter-by-letter typing
- Hyphens and spaces ignored for character count
- Uppercase or normal case
- Configurable ending
- Optional full number at end

**Examples**: 
- `O!` `N!` `E!` (letter-by-letter)
- `O!` `N!` `E!` `ONE!` (with add_full_number enabled)
- `ONE!` (full uppercase)

### GJs (Grammar Jacks)
- Normal sentence output
- Configurable ending (. or !)
- Case options (upper, lower, normal)

**Example**: `one hundred twenty-two.`

## Configuration

The system uses a `config.json` file (auto-created on first run):

```json
{
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
    "type": ".",
    "special_keys": {
      "type": "shift_r"
    }
  },
  "auto_jumping": false,
  "automatic_mode": {
    "enabled": false,
    "min_delay": 2.0,
    "max_delay": 5.0
  },
  "styles": {
    "JJs": {
      "ending": ".",
      "case": "capitalize"
    },
    "HJs": {
      "ending": "!",
      "case": "normal",
      "add_full_number": true
    },
    "GJs": {
      "ending": ".",
      "case": "capitalize"
    }
  },
  "debug": {
    "level": 0,
    "show_index": true,
    "show_formatted": true,
    "verbose": false,
    "show_keys": false
  }
}
```

### Configuration Options

#### Navigation
- **type**: Regular character key for typing (e.g., ".")
- **special_keys.type**: Special key name (e.g., "shift_r", "ctrl_l")

#### Auto-Jumping
- **auto_jumping**: When true, presses space, waits 100ms, then types (default: false)

#### Automatic Mode
- **enabled**: Enable/disable automatic typing mode
- **min_delay/max_delay**: Random delay range between auto-typings (seconds)

#### HJs Style Options
- **add_full_number**: When true, adds full number at end after letter-by-letter (default: true)

#### Debug Levels
- **0**: No debug output
- **1**: Basic debug (errors, auto mode timing)
- **2**: Detailed debug (includes key detection)

#### Special Key Names
Common special keys: `shift_r`, `shift_l`, `ctrl_r`, `ctrl_l`, `alt_r`, `alt_l`, `cmd_r`, `cmd_l`, `caps_lock`, `esc`, `space`, `enter`, `backspace`, `tab`, `delete`, `home`, `end`, `page_up`, `page_down`, `insert`, `num_lock`, `pause`, `scroll_lock`, `up`, `down`, `left`, `right`
```

### Configuration Options

#### Navigation
- **type**: Regular character key for typing (e.g., ".")
- **special_keys.type**: Special key name (e.g., "shift_r", "ctrl_l")

#### Automatic Mode
- **enabled**: Enable/disable automatic typing mode
- **min_delay/max_delay**: Random delay range between auto-typings (seconds)

#### Debug Levels
- **0**: No debug output
- **1**: Basic debug (errors, auto mode timing)
- **2**: Detailed debug (includes key detection)

#### Special Key Names
Common special keys: `shift_r`, `shift_l`, `ctrl_r`, `ctrl_l`, `alt_r`, `alt_l`, `cmd_r`, `cmd_l`, `caps_lock`, `esc`, `space`, `enter`, `backspace`, `tab`, `delete`, `home`, `end`, `page_up`, `page_down`, `insert`, `num_lock`, `pause`, `scroll_lock`, `up`, `down`, `left`, `right`

## Interactive Controls

When running, use these keys (press anywhere with pynput installed):

### Normal Mode
- **<type_key>** (default: `.`): Type current number with configured style
- **n**: Next number
- **p**: Previous number  
- **j**: Jump to specific number
- **q**: Quit
- **ESC**: Quit (always available)

### Automatic Mode
When `"automatic_mode.enabled": true`:
- **<type_key>** (default: `.`): Start automatic typing (types continuously with random delays)
- **ESC**: Quit (stops automatic typing)

### Special Keys (Optional)
You can configure special keys like Right Shift in the config:
```json
{
  "navigation": {
    "special_keys": {
      "type": "shift_r"    // Right Shift acts as type key
    }
  }
}
```

Available special keys include: `shift_r`, `shift_l`, `ctrl_r`, `ctrl_l`, `alt_r`, `alt_l`, etc.

## Command Line Options

```
usage: main.py [-h] [-l LANGUAGE] [-s {JJs,HJs,GJs}] [-c CONFIG]
               [--list-languages] [--validate] [--debug LEVEL]

AutoJJs - Auto-typing jack system for Linux Wayland

options:
  -h, --help            show this help message and exit
  -l LANGUAGE, --language LANGUAGE
                        Language to use (e.g., en, ptbr)
  -s {JJs,HJs,GJs}, --style {JJs,HJs,GJs}
                        Jack style to use
  -c CONFIG, --config CONFIG
                        Configuration file path (default: config.json)
  --list-languages      List all available languages and exit
  --validate            Validate configuration and language files
  --debug LEVEL         Enable debug mode (1=basic, 2=detailed with key detection)
```

## Troubleshooting

### Permission Denied
Make sure uinput module is loaded and you're in the input group:
```bash
sudo modprobe uinput
sudo usermod -a -G input $USER
# Then logout and login again
```

### Language Not Found
Check that the language folder has the correct structure:
```
languages/your_lang/numbers.json
```

### Debug Mode
Run with `--debug` flag for detailed error information:
```bash
./main.py --debug 1          # Basic debug
./main.py --debug 2          # Detailed debug with key detection
```

### Global Key Detection Issues
If global key detection doesn't work on Wayland:
1. Ensure pynput is installed properly
2. Try running with XWayland if available
3. Use terminal mode as fallback
4. Check Wayland compositor permissions

Tip: You can try using Right Shift (shift_r) as a special key.
For example, pressing Alt + key (= is the default) might work depending on your global key settings.

On KDE, you can adjust this in System Settings → Shortcuts → Global Shortcuts:
- Enable the option “Any key pressed while Ctrl, Alt, or Meta is also pressed”
- Or just set it to “Always allowed”

This way, your global key detection should behave consistently across Wayland sessions.


## Development

### Architecture

- **KeyboardSimulator**: Handles uinput device management and key events
- **LanguageManager**: Dynamic loading and validation of language files
- **JackStyle**: Abstract base for style implementations
- **NumberFlow**: Main application logic and user interaction
- **ConfigManager**: JSON-based configuration with validation

### Adding New Styles

1. Create a new class inheriting from `JackStyle`
2. Implement the `format()` method
3. Register it in `StyleManager`
4. Add configuration options

Example:
```python
class CustomStyle(JackStyle):
    def get_name(self) -> str:
        return "Custom"
    
    def format(self, text: str) -> List[str]:
        # Your formatting logic here
        return [formatted_text]
```