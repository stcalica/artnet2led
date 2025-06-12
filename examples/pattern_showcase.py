#!/usr/bin/env python3
"""
Pattern showcase example.

This script demonstrates all available patterns in the WS2812B DMX library.
"""

from ws2812b_dmx import (
    WS2812BController, ChasePattern, StrobePattern, RainbowPattern,
    WavePattern, SolidColorPattern
)
from ws2812b_dmx.constants import WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA


def main():
    """Run a showcase of all patterns."""
    print("WS2812B DMX Pattern Showcase")
    print("=" * 40)
    
    # Create controller
    controller = WS2812BController()
    
    try:
        # Discover fixtures
        print("Discovering WLED fixtures...")
        fixtures = controller.discover_fixtures()
        
        if not fixtures:
            print("No fixtures found. Exiting.")
            return
        
        print(f"Found {len(fixtures)} fixtures:")
        for fixture in fixtures:
            print(f"  - {fixture.name} at {fixture.ip} ({fixture.pixel_count} pixels)")
        
        # Pattern showcase
        patterns = [
            ("Solid Red", SolidColorPattern(fixtures, RED)),
            ("Solid Green", SolidColorPattern(fixtures, GREEN)),
            ("Solid Blue", SolidColorPattern(fixtures, BLUE)),
            ("White Chase", ChasePattern(fixtures, WHITE)),
            ("Red Chase", ChasePattern(fixtures, RED)),
            ("Green Chase", ChasePattern(fixtures, GREEN)),
            ("Blue Chase", ChasePattern(fixtures, BLUE)),
            ("White Strobe", StrobePattern(fixtures, WHITE)),
            ("Rainbow", RainbowPattern(fixtures, speed=0.5)),
            ("Fast Rainbow", RainbowPattern(fixtures, speed=2.0)),
            ("Blue Wave", WavePattern(fixtures, BLUE, frequency=1.0, amplitude=0.7)),
            ("Green Wave", WavePattern(fixtures, GREEN, frequency=2.0, amplitude=0.5)),
        ]
        
        print(f"\nRunning {len(patterns)} patterns for 5 seconds each...")
        print("Press Ctrl+C to stop early\n")
        
        for i, (name, pattern) in enumerate(patterns, 1):
            print(f"{i:2d}. {name}")
            try:
                controller.run_pattern(pattern, fps=30, duration=5.0)
            except KeyboardInterrupt:
                print("\nStopped by user")
                break
        
        print("\nShowcase complete!")
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.close()


if __name__ == "__main__":
    main() 