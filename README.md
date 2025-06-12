# Art-Net LED Controller Library

A Python library for controlling LED fixtures using Art-Net protocol over Ethernet networks.

## Features

- **Automatic Device Discovery**: Discover WLED fixtures on your local network using UDP broadcast
- **Art-Net Protocol Support**: Send DMX data to fixtures using the Art-Net protocol over Ethernet
- **Multiple Pattern Types**: Built-in patterns including chase, strobe, rainbow, wave, and solid color
- **Extensible Pattern System**: Easy to create custom patterns by extending the BasePattern class
- **Multi-Fixture Support**: Control multiple fixtures simultaneously with automatic universe assignment
- **Real-time Control**: High-performance pattern generation and transmission
- **Comprehensive Logging**: Built-in logging for debugging and monitoring

## Installation

### From Source

```bash
git clone https://github.com/yourusername/artnet-led-controller.git
cd artnet-led-controller
pip install -e .
```

### From PyPI (when published)

```bash
pip install artnet-led-controller
```

## Quick Start

```python
from artnet_led_controller import ArtNetController, ChasePattern
from artnet_led_controller.constants import RED

# Create controller and discover fixtures
controller = ArtNetController()
fixtures = controller.discover_fixtures()

# Create and run a chase pattern
pattern = ChasePattern(fixtures, color=RED)
controller.run_pattern(pattern, fps=30, duration=10.0)
```

## Basic Usage

### 1. Discover Fixtures

```python
from artnet_led_controller import ArtNetController

controller = ArtNetController()
fixtures = controller.discover_fixtures()

print(f"Found {len(fixtures)} fixtures:")
for fixture in fixtures:
    print(f"  - {fixture.name} at {fixture.ip} ({fixture.pixel_count} pixels)")
```

### 2. Run Built-in Patterns

```python
from artnet_led_controller import ChasePattern, StrobePattern, RainbowPattern

# Chase pattern (moving light)
chase = ChasePattern(fixtures, color=(255, 0, 0))  # Red
controller.run_pattern(chase, fps=30, duration=10.0)

# Strobe pattern (flashing)
strobe = StrobePattern(fixtures, color=(255, 255, 255))  # White
controller.run_pattern(strobe, fps=10, duration=5.0)

# Rainbow pattern
rainbow = RainbowPattern(fixtures, speed=1.0)
controller.run_pattern(rainbow, fps=30, duration=15.0)
```

### 3. Create Custom Patterns

```python
from artnet_led_controller import BasePattern
import math

class BreathingPattern(BasePattern):
    def __init__(self, fixture_manager, color=(255, 255, 255), speed=1.0):
        super().__init__(fixture_manager)
        self.color = color
        self.speed = speed

    def generate_frame(self):
        brightness = 0.3 + 0.7 * math.sin(self.step * self.speed / 30)
        rgb = tuple(int(c * brightness) for c in self.color)
        return list(rgb) * self.total_pixels

# Use the custom pattern
breathing = BreathingPattern(fixtures, color=(0, 255, 0), speed=1.0)
controller.run_pattern(breathing, fps=30, duration=20.0)
```

## Available Patterns

### Built-in Patterns

- **ChasePattern**: Single moving light that travels along the LED strip
- **StrobePattern**: All lights flash on and off
- **RainbowPattern**: Smooth color transition across all LEDs
- **WavePattern**: Sine wave of brightness across the LED strip
- **SolidColorPattern**: All LEDs display the same color

### Pattern Parameters

Each pattern accepts different parameters:

```python
# Chase pattern
ChasePattern(fixtures, color=(255, 0, 0))  # Red chase

# Rainbow pattern
RainbowPattern(fixtures, speed=1.0)  # Speed of color transition

# Wave pattern
WavePattern(fixtures, color=(0, 0, 255), frequency=1.0, amplitude=0.5)

# Solid color pattern
SolidColorPattern(fixtures, color=(255, 255, 0))  # Yellow
```

## Advanced Usage

### Manual Fixture Management

```python
# Add fixtures manually
controller.add_fixture_manually("192.168.1.100", 60, "Living Room")
controller.add_fixture_manually("192.168.1.101", 30, "Bedroom")

# Get fixture information
fixture_info = controller.get_fixture_info()
for info in fixture_info:
    print(f"Fixture: {info['name']} at {info['ip']}")
    print(f"  Pixels: {info['pixel_count']}")
    print(f"  Universe: {info['universe']}")
```

### Pattern Callbacks

```python
def frame_callback(frame_count, frame_data, fixtures_data):
    print(f"Frame {frame_count}: {len(fixtures_data)} fixtures")

pattern = ChasePattern(fixtures, color=(255, 0, 0))
controller.run_pattern(pattern, fps=30, callback=frame_callback)
```

### Context Manager Usage

```python
with ArtNetController() as controller:
    fixtures = controller.discover_fixtures()
    pattern = ChasePattern(fixtures, color=(0, 255, 0))
    controller.run_pattern(pattern, fps=30, duration=10.0)
# Controller automatically closes and turns off all fixtures
```

## Examples

Check out the `examples/` directory for complete working examples:

- `simple_chase.py`: Basic chase pattern demonstration
- `pattern_showcase.py`: Showcase of all built-in patterns
- `custom_pattern.py`: Examples of custom pattern creation

## Network Setup

This library is designed for a setup where:

- A Raspberry Pi (or any computer) is connected via Ethernet to a Power-over-Ethernet (PoE) switch
- The PoE switch provides both data and power to WLED-based LED controllers
- All devices are on the same local network

### Requirements

- WLED firmware on your LED controllers
- All devices on the same local network
- UDP broadcast enabled (usually default)
- Art-Net protocol support in WLED

## API Reference

### ArtNetController

Main controller class for managing fixtures and running patterns.

#### Methods

- `discover_fixtures()`: Discover WLED devices on the network
- `add_fixture_manually(ip, pixel_count, name)`: Add a fixture manually
- `run_pattern(pattern, fps, duration, callback)`: Run a pattern
- `run_pattern_simple(pattern_name, fps, duration, **kwargs)`: Run a pattern by name
- `stop_all_fixtures()`: Turn off all fixtures
- `get_fixture_info()`: Get information about all fixtures
- `close()`: Clean up resources

### BasePattern

Abstract base class for creating custom patterns.

#### Methods

- `generate_frame()`: Generate a single frame of pixel data
- `next_frame()`: Generate the next frame and advance the pattern
- `reset()`: Reset the pattern to its initial state
- `get_fixture_data(frame_data)`: Split frame data into fixture-specific data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- WLED project for the excellent firmware
- Art-Net protocol specification
- DMX512 standard

## Support

If you encounter any issues or have questions:

1. Check the [issues page](https://github.com/yourusername/artnet-led-controller/issues)
2. Create a new issue with detailed information
3. Include your network setup and WLED configuration
