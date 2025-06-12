#!/usr/bin/env python3
"""
Custom pattern example.

This script demonstrates how to create custom patterns by extending
the BasePattern class.
"""

from ws2812b_dmx import WS2812BController, BasePattern
from ws2812b_dmx.constants import WHITE, BLACK, RED, GREEN, BLUE
import math


class BreathingPattern(BasePattern):
    """
    Breathing pattern - lights fade in and out like breathing.
    """
    
    def __init__(self, fixture_manager, color=(255, 255, 255), speed=1.0):
        super().__init__(fixture_manager)
        self.color = color
        self.speed = speed
    
    def generate_frame(self):
        """Generate a breathing frame."""
        # Calculate brightness using sine wave for smooth breathing effect
        brightness = 0.3 + 0.7 * math.sin(self.step * self.speed / 30)
        
        # Apply brightness to color
        rgb = tuple(int(c * brightness) for c in self.color)
        return list(rgb) * self.total_pixels


class AlternatingPattern(BasePattern):
    """
    Alternating pattern - every other pixel is on/off.
    """
    
    def __init__(self, fixture_manager, color1=WHITE, color2=BLACK):
        super().__init__(fixture_manager)
        self.color1 = color1
        self.color2 = color2
    
    def generate_frame(self):
        """Generate an alternating frame."""
        data = []
        for i in range(self.total_pixels):
            if i % 2 == 0:
                data.extend(self.color1)
            else:
                data.extend(self.color2)
        return data


class PulsePattern(BasePattern):
    """
    Pulse pattern - lights pulse from center outward.
    """
    
    def __init__(self, fixture_manager, color=WHITE, speed=1.0):
        super().__init__(fixture_manager)
        self.color = color
        self.speed = speed
    
    def generate_frame(self):
        """Generate a pulse frame."""
        data = []
        center = self.total_pixels // 2
        
        for i in range(self.total_pixels):
            # Calculate distance from center
            distance = abs(i - center)
            
            # Calculate pulse wave
            pulse = math.sin((self.step * self.speed / 20) - (distance * 0.3))
            brightness = max(0, pulse * 0.5 + 0.5)
            
            # Apply brightness to color
            rgb = tuple(int(c * brightness) for c in self.color)
            data.extend(rgb)
        
        return data


def main():
    """Run custom pattern examples."""
    print("WS2812B DMX Custom Pattern Example")
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
        
        # Custom patterns
        custom_patterns = [
            ("White Breathing", BreathingPattern(fixtures, WHITE, speed=1.0)),
            ("Red Breathing", BreathingPattern(fixtures, RED, speed=1.5)),
            ("Blue Breathing", BreathingPattern(fixtures, BLUE, speed=0.8)),
            ("Red/Black Alternating", AlternatingPattern(fixtures, RED, BLACK)),
            ("White/Blue Alternating", AlternatingPattern(fixtures, WHITE, BLUE)),
            ("White Pulse", PulsePattern(fixtures, WHITE, speed=1.0)),
            ("Green Pulse", PulsePattern(fixtures, GREEN, speed=1.5)),
        ]
        
        print(f"\nRunning {len(custom_patterns)} custom patterns for 8 seconds each...")
        print("Press Ctrl+C to stop early\n")
        
        for i, (name, pattern) in enumerate(custom_patterns, 1):
            print(f"{i:2d}. {name}")
            try:
                controller.run_pattern(pattern, fps=30, duration=8.0)
            except KeyboardInterrupt:
                print("\nStopped by user")
                break
        
        print("\nCustom pattern demonstration complete!")
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.close()


if __name__ == "__main__":
    main() 