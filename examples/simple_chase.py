#!/usr/bin/env python3
"""
Simple chase pattern example.

This script demonstrates the basic usage of the WS2812B DMX library
to run a chase pattern across discovered WLED fixtures.
"""

from ws2812b_dmx import WS2812BController, ChasePattern
from ws2812b_dmx.constants import RED, GREEN, BLUE


def main():
    """Run a simple chase pattern."""
    print("WS2812B DMX Chase Pattern Example")
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
        
        # Create chase pattern with red color
        print("\nStarting red chase pattern...")
        pattern = ChasePattern(fixtures, color=RED)
        
        # Run the pattern for 10 seconds
        controller.run_pattern(pattern, fps=30, duration=10.0)
        
        # Try different colors
        colors = [GREEN, BLUE, RED]
        color_names = ["Green", "Blue", "Red"]
        
        for color, name in zip(colors, color_names):
            print(f"\nStarting {name.lower()} chase pattern...")
            pattern = ChasePattern(fixtures, color=color)
            controller.run_pattern(pattern, fps=30, duration=5.0)
        
        print("\nPattern demonstration complete!")
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.close()


if __name__ == "__main__":
    main() 