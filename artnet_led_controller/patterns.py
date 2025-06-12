"""
LED pattern generation module.

Provides base pattern class and specific pattern implementations for LED animations.
"""

import math
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
from .constants import WHITE, BLACK, RED, GREEN, BLUE


class BasePattern(ABC):
    """
    Abstract base class for LED patterns.
    
    All pattern classes should inherit from this and implement the required methods.
    """
    
    def __init__(self, fixture_manager):
        """
        Initialize pattern with fixture manager.
        
        Args:
            fixture_manager: FixtureManager instance containing fixtures
        """
        self.fixture_manager = fixture_manager
        self.total_pixels = fixture_manager.get_total_pixels()
        self.step = 0
    
    @abstractmethod
    def generate_frame(self) -> List[int]:
        """
        Generate a single frame of pixel data.
        
        Returns:
            List of RGB values for all pixels across all fixtures
        """
        pass
    
    def next_frame(self) -> List[int]:
        """
        Generate the next frame and advance the pattern step.
        
        Returns:
            List of RGB values for the next frame
        """
        frame_data = self.generate_frame()
        self.step += 1
        return frame_data
    
    def reset(self):
        """Reset the pattern to its initial state."""
        self.step = 0
    
    def get_fixture_data(self, frame_data: List[int]) -> List[Tuple]:
        """
        Split frame data into fixture-specific data.
        
        Args:
            frame_data: Complete frame data for all fixtures
            
        Returns:
            List of (fixture, pixel_data) tuples
        """
        fixtures_data = []
        pixel_offset = 0
        
        for fixture in self.fixture_manager:
            start_idx = pixel_offset * 3
            end_idx = (pixel_offset + fixture.pixel_count) * 3
            fixture_data = frame_data[start_idx:end_idx]
            fixtures_data.append((fixture, fixture_data))
            pixel_offset += fixture.pixel_count
        
        return fixtures_data


class ChasePattern(BasePattern):
    """
    Chase pattern - single moving light that travels along the LED strip.
    """
    
    def __init__(self, fixture_manager, color: Tuple[int, int, int] = WHITE):
        """
        Initialize chase pattern.
        
        Args:
            fixture_manager: FixtureManager instance
            color: Color of the moving light (RGB tuple)
        """
        super().__init__(fixture_manager)
        self.color = color
    
    def generate_frame(self) -> List[int]:
        """Generate a single chase frame."""
        data = []
        current_pixel = self.step % self.total_pixels
        
        for i in range(self.total_pixels):
            if i == current_pixel:
                data.extend(self.color)
            else:
                data.extend(BLACK)
        
        return data


class StrobePattern(BasePattern):
    """
    Strobe pattern - all lights flash on and off.
    """
    
    def __init__(self, fixture_manager, color: Tuple[int, int, int] = WHITE):
        """
        Initialize strobe pattern.
        
        Args:
            fixture_manager: FixtureManager instance
            color: Color for the strobe effect (RGB tuple)
        """
        super().__init__(fixture_manager)
        self.color = color
    
    def generate_frame(self) -> List[int]:
        """Generate a single strobe frame."""
        # Alternate between all on and all off
        is_on = (self.step % 2) == 0
        if is_on:
            return list(self.color) * self.total_pixels
        else:
            return list(BLACK) * self.total_pixels


class RainbowPattern(BasePattern):
    """
    Rainbow pattern - smooth color transition across all LEDs.
    """
    
    def __init__(self, fixture_manager, speed: float = 1.0):
        """
        Initialize rainbow pattern.
        
        Args:
            fixture_manager: FixtureManager instance
            speed: Speed of color transition (higher = faster)
        """
        super().__init__(fixture_manager)
        self.speed = speed
    
    def generate_frame(self) -> List[int]:
        """Generate a single rainbow frame."""
        data = []
        
        for i in range(self.total_pixels):
            # Calculate hue based on position and time
            # Position component: (i / self.total_pixels) - spreads rainbow across pixels
            # Time component: ((self.step * self.speed) / 100) - moves rainbow over time
            hue = ((i / self.total_pixels) + ((self.step * self.speed) / 100)) % 1.0
            rgb = self._hsv_to_rgb(hue, 1.0, 1.0)
            data.extend(rgb)
        
        return data
    
    def _hsv_to_rgb(self, hue: float, saturation: float, value: float) -> Tuple[int, int, int]:
        """
        Convert HSV (Hue, Saturation, Value) color to RGB (Red, Green, Blue).
        
        HSV is easier for creating smooth color transitions like rainbows.
        RGB is what LED strips actually use.
        
        Args:
            hue: Color position in rainbow (0.0 = red, 0.33 = green, 0.67 = blue, 1.0 = red again)
            saturation: How colorful vs gray (0.0 = gray, 1.0 = full color)
            value: Brightness (0.0 = black, 1.0 = full brightness)
            
        Returns:
            RGB tuple with values 0-255 for each color channel
        """
        # Handle grayscale case (no color, just brightness)
        if saturation == 0.0:
            gray_value = int(value * 255)
            return (gray_value, gray_value, gray_value)
        
        # Convert hue (0.0-1.0) to color sector (0-5)
        # The color wheel is divided into 6 sectors: Red, Yellow, Green, Cyan, Blue, Magenta
        color_sector = int(hue * 6.0)
        
        # Calculate how far through the current color sector we are (0.0-1.0)
        # This determines the mixing between the two primary colors in this sector
        sector_fraction = (hue * 6.0) - color_sector
        
        # Calculate the three RGB components for this HSV value
        # These formulas create smooth transitions between colors
        min_rgb_value = value * (1.0 - saturation)                    # Darkest component
        mid_rgb_value_1 = value * (1.0 - (saturation * sector_fraction))  # First intermediate
        mid_rgb_value_2 = value * (1.0 - (saturation * (1.0 - sector_fraction)))  # Second intermediate
        
        # Ensure color sector is 0-5 (handles edge case when hue = 1.0)
        color_sector = color_sector % 6
        
        # Assign RGB values based on which color sector we're in
        # Each sector has one color at maximum, one at minimum, and one intermediate
        if color_sector == 0:      # Red to Yellow sector
            red, green, blue = value, mid_rgb_value_2, min_rgb_value
        elif color_sector == 1:    # Yellow to Green sector  
            red, green, blue = mid_rgb_value_1, value, min_rgb_value
        elif color_sector == 2:    # Green to Cyan sector
            red, green, blue = min_rgb_value, value, mid_rgb_value_2
        elif color_sector == 3:    # Cyan to Blue sector
            red, green, blue = min_rgb_value, mid_rgb_value_1, value
        elif color_sector == 4:    # Blue to Magenta sector
            red, green, blue = mid_rgb_value_2, min_rgb_value, value
        else:                       # Magenta to Red sector (color_sector == 5)
            red, green, blue = value, min_rgb_value, mid_rgb_value_1
        
        # Convert from 0.0-1.0 range to 0-255 range for LED strips
        return (int(red * 255), int(green * 255), int(blue * 255))


class WavePattern(BasePattern):
    """
    Wave pattern - sine wave of brightness across the LED strip.
    """
    
    def __init__(self, fixture_manager, color: Tuple[int, int, int] = WHITE, 
                 frequency: float = 1.0, amplitude: float = 0.5):
        """
        Initialize wave pattern.
        
        Args:
            fixture_manager: FixtureManager instance
            color: Base color for the wave (RGB tuple)
            frequency: Frequency of the wave
            amplitude: Amplitude of the wave (0.0 to 1.0)
        """
        super().__init__(fixture_manager)
        self.color = color
        self.frequency = frequency
        self.amplitude = amplitude
    
    def generate_frame(self) -> List[int]:
        """Generate a single wave frame."""
        data = []
        
        for i in range(self.total_pixels):
            # Calculate brightness using sine wave
            position = i / self.total_pixels
            time_offset = self.step / 100
            brightness = 0.5 + self.amplitude * math.sin(2 * math.pi * (position + time_offset * self.frequency))
            
            # Apply brightness to color
            rgb = tuple(int(c * brightness) for c in self.color)
            data.extend(rgb)
        
        return data


class SolidColorPattern(BasePattern):
    """
    Solid color pattern - all LEDs display the same color.
    """
    
    def __init__(self, fixture_manager, color: Tuple[int, int, int] = WHITE):
        """
        Initialize solid color pattern.
        
        Args:
            fixture_manager: FixtureManager instance
            color: Color to display (RGB tuple)
        """
        super().__init__(fixture_manager)
        self.color = color
    
    def generate_frame(self) -> List[int]:
        """Generate a solid color frame."""
        return list(self.color) * self.total_pixels 