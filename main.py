import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config.config_manager import ConfigManager
from src.core.number_flow import NumberFlow
from src.core.language_manager import LanguageManager

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    keyboard = None
    PYNPUT_AVAILABLE = False


def main():
    parser = argparse.ArgumentParser(
        description="AutoJJs - Auto-typing jack system for Linux Wayland",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start with default configuration
  %(prog)s -l ptbr           # Start with Portuguese Brazilian
  %(prog)s -s HJs           # Start with HJs style
  %(prog)s --list-languages  # Show available languages
  %(prog)s --validate       # Validate current configuration
  %(prog)s --debug 1        # Enable basic debug mode
  %(prog)s --debug 2        # Enable detailed debug with key detection
        """
    )
    
    parser.add_argument('-l', '--language', 
                       help='Language to use (e.g., en, ptbr)')
    parser.add_argument('-s', '--style', 
                       choices=['JJs', 'HJs', 'GJs'],
                       help='Jack style to use')
    parser.add_argument('-c', '--config', 
                       default='config.json',
                       help='Configuration file path (default: config.json)')
    parser.add_argument('--list-languages', action='store_true',
                       help='List all available languages and exit')
    parser.add_argument('--validate', action='store_true',
                       help='Validate configuration and language files')
    parser.add_argument('--debug', type=int, choices=[1, 2], metavar='LEVEL',
                        help='Enable debug mode (1=basic, 2=detailed with key detection)')
    
    args = parser.parse_args()
    
    try:
        config = ConfigManager(args.config)
        
        if args.debug:
            config.set('debug.level', args.debug)
            config.set('debug.verbose', True)
            if args.debug >= 2:
                config.set('debug.show_keys', True)
        
        if args.validate:
            return validate_system(config)
        
        if args.list_languages:
            return list_languages(config)
        
        if args.language:
            config.set_language(args.language)
        
        if args.style:
            config.set_jack_style(args.style)
        
        validation = config.validate_config()
        if not validation['valid']:
            print("Configuration errors:")
            for error in validation['errors']:
                print(f"  - {error}")
            return 1
        
        flow = NumberFlow(config)
        
        if not PYNPUT_AVAILABLE:
            print("Note: pynput not available. Global key detection disabled.")
            print("Install with: pip install pynput")
            print("Or run in terminal mode only.\n")
        
        flow.start()
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def validate_system(config: ConfigManager) -> int:
    print("=== System Validation ===\n")
    
    config_validation = config.validate_config()
    if not config_validation['valid']:
        print("Configuration errors:")
        for error in config_validation['errors']:
            print(f"  Err: {error}")
        return 1
    else:
        print("✅ Configuration is valid")
    
    if config_validation['warnings']:
        print("\nConfiguration warnings:")
        for warning in config_validation['warnings']:
            print(f"  ⚠️  {warning}")
    
    print(f"\nLanguage: {config.get_language()}")
    print(f"Style: {config.get_jack_style()}")
    print(f"Prefix key: {config.get_prefix_key()}")
    
    lang_manager = LanguageManager()
    available = lang_manager.get_available_languages()
    
    if not available:
        print("Err: No languages found")
        return 1
    
    print(f"\nAvailable languages: {', '.join(available)}")
    
    if config.get_language() not in available:
        print(f"Err: Language '{config.get_language()}' not available")
        return 1
    
    lang_validation = lang_manager.validate_language_structure(config.get_language())
    if not lang_validation['valid']:
        print(f"Language '{config.get_language()}' errors:")
        for error in lang_validation['errors']:
            print(f"  Err: {error}")
        return 1
    else:
        print(f"✅ Language '{config.get_language()}' is valid")
    
    if lang_validation['warnings']:
        print(f"Language '{config.get_language()}' warnings:")
        for warning in lang_validation['warnings']:
            print(f"  ⚠️  {warning}")
    
    if not lang_manager.load_language(config.get_language()):
        print(f"Err: Failed to load language '{config.get_language()}'")
        return 1
    
    total = lang_manager.get_total_numbers()
    print(f"✅ Loaded {total} numbers")
    
    print("\n=== Validation Complete ===")
    return 0


def list_languages(config: ConfigManager) -> int:
    print("=== Available Languages ===\n")
    
    lang_manager = LanguageManager()
    available = lang_manager.get_available_languages()
    
    if not available:
        print("No languages found.")
        print("Create language directories in 'languages/' folder.")
        return 1
    
    for lang_code in sorted(available):
        validation = lang_manager.validate_language_structure(lang_code)
        
        if validation['valid']:
            status = "✅"
        else:
            status = "Err:"
        
        print(f"{status} {lang_code}")
        
        if validation['errors']:
            for error in validation['errors']:
                print(f"    Error: {error}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"    Warning: {warning}")
        
        if lang_manager.load_language(lang_code):
            total = lang_manager.get_total_numbers()
            print(f"    Numbers: {total}")
        
        print()
    
    print(f"Current language: {config.get_language()}")
    return 0


if __name__ == '__main__':
    sys.exit(main())