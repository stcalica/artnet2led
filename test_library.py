#!/usr/bin/env python3
"""
Simple test script to verify the Art-Net LED Controller library structure.
"""

import sys
import os

# Add the current directory to the path so we can import the library
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing library imports...")
    
    try:
        from artnet_led_controller import (
            ArtNetController, ChasePattern, StrobePattern, RainbowPattern,
            WavePattern, SolidColorPattern, BasePattern
        )
        print("✓ Main library imports successful")
        
        from artnet_led_controller.constants import WHITE, RED, GREEN, BLUE
        print("✓ Constants imports successful")
        
        from artnet_led_controller.discovery import WLEDDiscovery
        print("✓ Discovery module imports successful")
        
        from artnet_led_controller.fixture import Fixture, FixtureManager
        print("✓ Fixture module imports successful")
        
        from artnet_led_controller.artnet import ArtNetSender
        print("✓ Art-Net module imports successful")
        
        from artnet_led_controller.patterns import BasePattern
        print("✓ Patterns module imports successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_controller_creation():
    """Test controller creation."""
    print("\nTesting controller creation...")
    
    try:
        from artnet_led_controller import ArtNetController
        
        controller = ArtNetController()
        print("✓ Controller created successfully")
        
        # Test fixture manager
        fixtures = controller.fixture_manager
        print(f"✓ Fixture manager initialized with {len(fixtures)} fixtures")
        
        controller.close()
        print("✓ Controller closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Controller creation error: {e}")
        return False

def test_pattern_creation():
    """Test pattern creation."""
    print("\nTesting pattern creation...")
    
    try:
        from artnet_led_controller import ArtNetController, ChasePattern, StrobePattern
        from artnet_led_controller.constants import RED
        
        controller = ArtNetController()
        
        # Create a mock fixture manager with one fixture
        from artnet_led_controller.fixture import FixtureManager
        fixture_manager = FixtureManager()
        fixture_manager.add_fixture("192.168.1.100", 60, "Test Fixture")
        
        # Test pattern creation
        chase = ChasePattern(fixture_manager, color=RED)
        print("✓ Chase pattern created successfully")
        
        strobe = StrobePattern(fixture_manager, color=RED)
        print("✓ Strobe pattern created successfully")
        
        # Test frame generation
        frame = chase.generate_frame()
        print(f"✓ Frame generated with {len(frame)} values")
        
        controller.close()
        return True
        
    except Exception as e:
        print(f"✗ Pattern creation error: {e}")
        return False

def test_constants():
    """Test constants."""
    print("\nTesting constants...")
    
    try:
        from artnet_led_controller.constants import WHITE, RED, GREEN, BLUE, DISCOVERY_PORT, ARTNET_PORT
        
        assert WHITE == (255, 255, 255)
        assert RED == (255, 0, 0)
        assert GREEN == (0, 255, 0)
        assert BLUE == (0, 0, 255)
        assert DISCOVERY_PORT == 21324
        assert ARTNET_PORT == 6454
        
        print("✓ All constants have correct values")
        return True
        
    except Exception as e:
        print(f"✗ Constants error: {e}")
        return False

def main():
    """Run all tests."""
    print("Art-Net LED Controller Library Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_controller_creation,
        test_pattern_creation,
        test_constants
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Library is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 