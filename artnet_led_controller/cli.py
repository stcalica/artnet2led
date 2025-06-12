#!/usr/bin/env python3
"""
Command-line interface for Art-Net LED Controller Library.
"""

import argparse
import sys
from . import ArtNetController
from .constants import WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, BLACK


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Art-Net LED Controller Library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover and list fixtures
  artnet-led-controller discover

  # Run a red chase pattern for 10 seconds
  artnet-led-controller run chase --color red --duration 10

  # Run a rainbow pattern
  artnet-led-controller run rainbow --speed 1.0

  # Run a strobe pattern
  artnet-led-controller run strobe --color white --fps 10

  # Run pattern without discovery (for commercial fixtures)
  artnet-led-controller run chase --no-discovery

  # Turn off all fixtures
  artnet-led-controller off

  # Blackout all fixtures (emergency stop)
  artnet-led-controller blackout

Note: Use --no-discovery when working with commercial Art-Net fixtures 
that don't support WLED discovery protocol.
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover WLED fixtures')
    discover_parser.add_argument('--timeout', type=float, default=2.0, 
                               help='Discovery timeout in seconds (default: 2.0)')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a pattern')
    run_parser.add_argument('pattern', choices=['chase', 'strobe', 'rainbow', 'wave', 'solid'],
                          help='Pattern to run')
    run_parser.add_argument('--color', default='white',
                          choices=['white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta'],
                          help='Color for the pattern (default: white)')
    run_parser.add_argument('--fps', type=int, default=30,
                          help='Frames per second (default: 30)')
    run_parser.add_argument('--duration', type=float,
                          help='Duration in seconds (default: run indefinitely)')
    run_parser.add_argument('--speed', type=float, default=1.0,
                          help='Pattern speed (for rainbow/wave patterns)')
    run_parser.add_argument('--frequency', type=float, default=1.0,
                          help='Wave frequency (for wave pattern)')
    run_parser.add_argument('--amplitude', type=float, default=0.5,
                          help='Wave amplitude (for wave pattern)')
    run_parser.add_argument('--no-discovery', action='store_true',
                          help='Skip WLED discovery (for commercial fixtures)')
    
    # Off command
    off_parser = subparsers.add_parser('off', help='Turn off all fixtures')
    
    # Blackout command
    blackout_parser = subparsers.add_parser('blackout', help='Emergency blackout - turn off all fixtures immediately')
    blackout_parser.add_argument('--force', action='store_true',
                               help='Force blackout even if no fixtures are discovered')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Color mapping
    color_map = {
        'white': WHITE,
        'red': RED,
        'green': GREEN,
        'blue': BLUE,
        'yellow': YELLOW,
        'cyan': CYAN,
        'magenta': MAGENTA
    }
    
    try:
        controller = ArtNetController()
        
        if args.command == 'discover':
            print("Discovering WLED fixtures...")
            fixtures = controller.discover_fixtures()
            
            if not fixtures:
                print("No fixtures found.")
                return 0
            
            print(f"\nFound {len(fixtures)} fixtures:")
            for fixture in fixtures:
                print(f"  - {fixture.name} at {fixture.ip}")
                print(f"    Pixels: {fixture.pixel_count}")
                print(f"    Universe: {fixture.universe}")
                print()
        
        elif args.command == 'run':
            # Handle discovery based on flag
            if args.no_discovery:
                print("Skipping WLED discovery - using manually configured fixtures only")
                controller.skip_discovery()
                
                if not controller.fixture_manager:
                    print("No fixtures configured. Add fixtures manually in code or use discovery.")
                    print("Example: controller.add_fixture_manually('192.168.1.100', 60, 'Fixture Name')")
                    return 1
            else:
                # Discover fixtures if not already done
                if not controller.fixture_manager:
                    print("Discovering fixtures...")
                    controller.discover_fixtures()
            
            if not controller.fixture_manager:
                print("No fixtures found. Cannot run pattern.")
                return 1
            
            # Create pattern
            pattern_kwargs = {}
            
            if args.pattern in ['chase', 'strobe', 'solid']:
                pattern_kwargs['color'] = color_map[args.color]
            elif args.pattern == 'rainbow':
                pattern_kwargs['speed'] = args.speed
            elif args.pattern == 'wave':
                pattern_kwargs['color'] = color_map[args.color]
                pattern_kwargs['frequency'] = args.frequency
                pattern_kwargs['amplitude'] = args.amplitude
            
            print(f"Running {args.pattern} pattern...")
            print(f"  Color: {args.color}")
            print(f"  FPS: {args.fps}")
            if args.duration:
                print(f"  Duration: {args.duration} seconds")
            else:
                print("  Duration: indefinite (press Ctrl+C to stop)")
            
            controller.run_pattern_simple(
                args.pattern,
                fps=args.fps,
                duration=args.duration,
                **pattern_kwargs
            )
        
        elif args.command == 'off':
            print("Turning off all fixtures...")
            controller.stop_all_fixtures()
            print("All fixtures turned off.")
        
        elif args.command == 'blackout':
            print("🚨 EMERGENCY BLACKOUT 🚨")
            print("Turning off all fixtures immediately...")
            
            # Try to discover fixtures if not already done
            if not controller.fixture_manager:
                print("Discovering fixtures for blackout...")
                controller.discover_fixtures()
            
            if not controller.fixture_manager and not args.force:
                print("No fixtures found. Use --force to blackout anyway.")
                return 1
            
            # Send blackout to all fixtures
            controller.stop_all_fixtures()
            
            # Additional blackout measures
            if controller.fixture_manager:
                print(f"✅ Blackout complete - {len(controller.fixture_manager)} fixtures turned off")
            else:
                print("✅ Blackout complete - no fixtures found")
            
            print("All fixtures are now OFF.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nStopped by user")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        if 'controller' in locals():
            controller.close()


if __name__ == '__main__':
    sys.exit(main()) 