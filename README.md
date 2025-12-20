# AutoJJs - Auto-typing Jack System

A modular Python system for Linux Wayland that uses the **uinput kernel module** to simulate keyboard input for typing numbers written in text form across unlimited languages.

## Features

- **Modular Architecture**: Clean, extensible design with separate components for keyboard input, language management, styling, and configuration
- **Unlimited Languages**: Add new languages by simply creating folders with JSON files - no code changes needed
- **Multiple Jack Styles**: JJs (sentence), HJs (letter-by-letter), and GJs (normal) with configurable formatting
- **Wayland Compatible**: Uses python-uinput for kernel-level keyboard simulation
- **Interactive Navigation**: Full control over number flow with next/previous/jump commands
- **Configuration Driven**: All settings configurable via JSON file

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
- Hyphens ignored for character count
- Uppercase or normal case
- Configurable ending

**Examples**: 
- `O!` `N!` `E!` (letter-by-letter)
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
    "quit": "q"
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
    "show_index": true,
    "show_formatted": true,
    "verbose": false
  }
}
```

## Interactive Controls

When running, use these keys:

- **Enter**: Type current number with configured style
- **n**: Next number
- **p**: Previous number  
- **j**: Jump to specific number
- **q**: Quit

## Command Line Options

```
usage: main.py [-h] [-l LANGUAGE] [-s {JJs,HJs,GJs}] [-c CONFIG]
               [--list-languages] [--validate] [--debug]

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
  --debug               Enable debug mode
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
./main.py --debug
```

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