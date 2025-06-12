"""
Main controller module for Art-Net LED controller.

Provides the high-level API for discovering fixtures and running patterns.
"""

import time
import logging
from datetime import datetime
from typing import List, Optional, Callable
from .discovery import WLEDDiscovery
from .fixture import FixtureManager, create_fixtures_from_discovery
from .artnet import ArtNetSender
from .patterns import BasePattern
from .constants import DEFAULT_FPS, DEFAULT_DISCOVERY_TIMEOUT


class ArtNetController:
    """
    Main controller class for Art-Net LED controller.
    
    This class provides the high-level API for discovering WLED fixtures
    and running LED patterns across multiple fixtures.
    """
    
    def __init__(self, discovery_timeout: float = DEFAULT_DISCOVERY_TIMEOUT):
        """
        Initialize the Art-Net controller.
        
        Args:
            discovery_timeout: Timeout for device discovery in seconds
        """
        self.discovery = WLEDDiscovery(discovery_timeout)
        self.fixture_manager = FixtureManager()
        self.artnet_sender = ArtNetSender()
        self.logger = logging.getLogger(__name__)
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_filename = f"artnet_led_controller_{datetime.now().strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def discover_fixtures(self) -> FixtureManager:
        """
        Discover WLED fixtures on the network.
        
        Returns:
            FixtureManager with discovered fixtures
            
        Raises:
            Exception: If discovery fails
        """
        self.logger.info("Starting WLED device discovery...")
        
        discovered_devices = self.discovery.discover_devices()
        
        if not discovered_devices:
            self.logger.warning("No WLED devices found on the network")
            return self.fixture_manager
        
        # Create fixture manager from discovered devices
        self.fixture_manager = create_fixtures_from_discovery(discovered_devices)
        
        self.logger.info(f"Discovered {len(self.fixture_manager)} fixtures")
        for fixture in self.fixture_manager:
            self.logger.info(f"  - {fixture.name} at {fixture.ip} ({fixture.pixel_count} pixels, universe {fixture.universe})")
        
        return self.fixture_manager
    
    def skip_discovery(self) -> None:
        """
        Skip WLED discovery and work with manually added fixtures only.
        
        Use this when working with commercial Art-Net fixtures or other
        non-WLED devices that don't support the WLED discovery protocol.
        """
        self.logger.info("Skipping WLED discovery - using manually configured fixtures only")
        # Fixture manager is already initialized, just don't run discovery
    
    def add_fixture_manually(self, ip: str, pixel_count: int, name: Optional[str] = None) -> None:
        """
        Manually add a fixture without discovery.
        
        Args:
            ip: IP address of the fixture
            pixel_count: Number of pixels in the fixture
            name: Optional name for the fixture
        """
        self.fixture_manager.add_fixture(ip, pixel_count, name)
        self.logger.info(f"Manually added fixture: {name or ip} at {ip}")
    
    def run_pattern(self, pattern: BasePattern, fps: int = DEFAULT_FPS, 
                   duration: Optional[float] = None, callback: Optional[Callable] = None) -> None:
        """
        Run a pattern across all fixtures.
        
        Args:
            pattern: Pattern instance to run
            fps: Frames per second for the animation
            duration: Duration to run the pattern in seconds (None for infinite)
            callback: Optional callback function called each frame
        """
        if not self.fixture_manager:
            self.logger.error("No fixtures available. Run discover_fixtures() first.")
            return
        
        self.logger.info(f"Starting pattern: {pattern.__class__.__name__} at {fps} FPS")
        
        delay = 1.0 / fps
        start_time = time.time()
        frame_count = 0
        
        try:
            while True:
                frame_start = time.time()
                
                # Generate and send frame
                frame_data = pattern.next_frame()
                fixtures_data = pattern.get_fixture_data(frame_data)
                
                # Send to all fixtures
                success = self.artnet_sender.send_multiple_fixtures(fixtures_data)
                
                if not success:
                    self.logger.warning("Some fixtures failed to receive data")
                
                frame_count += 1
                
                # Call callback if provided
                if callback:
                    callback(frame_count, frame_data, fixtures_data)
                
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    self.logger.info(f"Pattern completed after {duration} seconds")
                    break
                
                # Calculate sleep time to maintain FPS
                frame_time = time.time() - frame_start
                sleep_time = max(0, delay - frame_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.logger.info("Pattern stopped by user")
        except Exception as e:
            self.logger.error(f"Error running pattern: {e}")
            raise
        finally:
            self.logger.info(f"Pattern finished. Sent {frame_count} frames")
    
    def run_pattern_simple(self, pattern_name: str, fps: int = DEFAULT_FPS, 
                          duration: Optional[float] = None, **pattern_kwargs) -> None:
        """
        Run a pattern by name with automatic fixture discovery.
        
        Args:
            pattern_name: Name of the pattern ('chase', 'strobe', 'rainbow', 'wave', 'solid')
            fps: Frames per second
            duration: Duration to run in seconds
            **pattern_kwargs: Additional arguments for the pattern
        """
        # Discover fixtures if not already done
        if not self.fixture_manager:
            self.discover_fixtures()
        
        # Create pattern based on name
        pattern = self._create_pattern_by_name(pattern_name, **pattern_kwargs)
        
        # Run the pattern
        self.run_pattern(pattern, fps, duration)
    
    def _create_pattern_by_name(self, pattern_name: str, **kwargs) -> BasePattern:
        """
        Create a pattern instance by name.
        
        Args:
            pattern_name: Name of the pattern
            **kwargs: Pattern-specific arguments
            
        Returns:
            Pattern instance
            
        Raises:
            ValueError: If pattern name is not recognized
        """
        from .patterns import (
            ChasePattern, StrobePattern, RainbowPattern, 
            WavePattern, SolidColorPattern
        )
        
        pattern_map = {
            'chase': ChasePattern,
            'strobe': StrobePattern,
            'rainbow': RainbowPattern,
            'wave': WavePattern,
            'solid': SolidColorPattern
        }
        
        if pattern_name not in pattern_map:
            raise ValueError(f"Unknown pattern: {pattern_name}. Available: {list(pattern_map.keys())}")
        
        pattern_class = pattern_map[pattern_name]
        return pattern_class(self.fixture_manager, **kwargs)
    
    def stop_all_fixtures(self) -> None:
        """Turn off all fixtures by sending black to all pixels."""
        if not self.fixture_manager:
            return
        
        from .patterns import SolidColorPattern
        from .constants import BLACK
        
        pattern = SolidColorPattern(self.fixture_manager, BLACK)
        frame_data = pattern.generate_frame()
        fixtures_data = pattern.get_fixture_data(frame_data)
        
        self.artnet_sender.send_multiple_fixtures(fixtures_data)
        self.logger.info("Turned off all fixtures")
    
    def get_fixture_info(self) -> List[dict]:
        """
        Get information about all fixtures.
        
        Returns:
            List of fixture information dictionaries
        """
        return [fixture.to_dict() for fixture in self.fixture_manager]
    
    def close(self):
        """Clean up resources."""
        self.stop_all_fixtures()
        self.artnet_sender.close()
        self.logger.info("Controller closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 