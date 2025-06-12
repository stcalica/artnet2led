"""
Art-Net LED Controller Library

A Python library for controlling LED fixtures using Art-Net protocol over Ethernet networks.

This library provides:
- WLED device discovery over UDP
- Art-Net packet generation and transmission
- Pattern generation for LED animations
- Fixture management and universe assignment

Example usage:
    from artnet_led_controller import ArtNetController, ChasePattern, StrobePattern
    
    # Create controller and discover fixtures
    controller = ArtNetController()
    fixtures = controller.discover_fixtures()
    
    # Create and run a pattern
    pattern = ChasePattern(fixtures)
    controller.run_pattern(pattern, fps=30)
"""

from .controller import ArtNetController
from .patterns import ChasePattern, StrobePattern, BasePattern
from .fixture import Fixture, FixtureManager
from .artnet import ArtNetSender
from .discovery import WLEDDiscovery

__version__ = "1.0.0"
__author__ = "Art-Net LED Controller Library"

__all__ = [
    'ArtNetController',
    'ChasePattern', 
    'StrobePattern',
    'BasePattern',
    'Fixture',
    'FixtureManager',
    'ArtNetSender',
    'WLEDDiscovery'
] 