"""
Fixture management module.

Handles individual fixture objects and universe assignment for DMX control.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Fixture:
    """
    Represents a single WLED fixture with its properties and configuration.
    We assume every fixture has a sttaic IP address and listens to it's own seperate universe.
    """
    ip: str
    pixel_count: int
    universe: int
    name: Optional[str] = None
    info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Set default name if not provided."""
        if self.name is None:
            self.name = f"Fixture-{self.ip}"
    
    @property
    def channel_count(self) -> int:
        """Get the total number of DMX channels for this fixture."""
        return self.pixel_count * 3  # 3 channels per RGB pixel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fixture to dictionary representation."""
        return {
            'ip': self.ip,
            'pixel_count': self.pixel_count,
            'universe': self.universe,
            'name': self.name,
            'channel_count': self.channel_count
        }


class FixtureManager:
    """
    Manages a collection of fixtures and handles universe assignment.
    """
    
    def __init__(self):
        """Initialize the fixture manager."""
        self.fixtures: List[Fixture] = []
        self.logger = logging.getLogger(__name__)
    
    def add_fixture(self, ip: str, pixel_count: int, name: Optional[str] = None, 
                   info: Optional[Dict[str, Any]] = None, universe: Optional[int] = None) -> Fixture:
        """
        Add a new fixture to the manager.
        
        Args:
            ip: IP address of the fixture
            pixel_count: Number of pixels in the fixture
            name: Optional name for the fixture
            info: Optional discovery info dictionary
            universe: Optional universe number (if None, uses IP-based assignment)
            
        Returns:
            The created Fixture object
        """
        # Use IP-based universe assignment if not provided
        if universe is None:
            universe = self._get_universe_from_ip(ip)
        
        fixture = Fixture(ip, pixel_count, universe, name, info)
        self.fixtures.append(fixture)
        self.logger.info(f"Added fixture: {fixture.name} at {ip} (universe {universe})")
        return fixture
    
    def _get_universe_from_ip(self, ip: str) -> int:
        """
        Get universe number from IP address.
        Uses the last octet of the IP as the universe number.
        
        Args:
            ip: IP address (e.g., "192.168.1.100")
            
        Returns:
            Universe number (e.g., 100)
        """
        try:
            # Extract last octet and use as universe
            universe = int(ip.split('.')[-1])
            self.logger.info(f"Assigned universe {universe} to IP {ip}")
            return universe
        except (ValueError, IndexError):
            # Fallback to sequential assignment if IP parsing fails
            universe = len(self.fixtures)
            self.logger.warning(f"Could not parse IP {ip}, using sequential universe {universe}")
            return universe
    
    def get_fixture_by_ip(self, ip: str) -> Optional[Fixture]:
        """Get a fixture by its IP address."""
        for fixture in self.fixtures:
            if fixture.ip == ip:
                return fixture
        return None
    
    def get_fixture_by_universe(self, universe: int) -> Optional[Fixture]:
        """Get a fixture by its universe number."""
        for fixture in self.fixtures:
            if fixture.universe == universe:
                return fixture
        return None
    
    def get_total_pixels(self) -> int:
        """Get the total number of pixels across all fixtures."""
        return sum(fixture.pixel_count for fixture in self.fixtures)
    
    def get_total_channels(self) -> int:
        """Get the total number of DMX channels across all fixtures."""
        return sum(fixture.channel_count for fixture in self.fixtures)
    
    def clear(self):
        """Remove all fixtures."""
        self.fixtures.clear()
        self.logger.info("Cleared all fixtures")
    
    def __len__(self) -> int:
        """Get the number of fixtures."""
        return len(self.fixtures)
    
    def __iter__(self):
        """Iterate over fixtures."""
        return iter(self.fixtures)
    
    def __getitem__(self, index: int) -> Fixture:
        """Get fixture by index."""
        return self.fixtures[index]


def create_fixtures_from_discovery(discovered_devices: List[tuple]) -> FixtureManager:
    """
    Create a FixtureManager from discovered WLED devices.
    
    Args:
        discovered_devices: List of (ip, info_dict) tuples from discovery
        
    Returns:
        FixtureManager with fixtures created from discovery results
    """
    manager = FixtureManager()
    
    for ip, info in discovered_devices:
        # Extract pixel count from WLED info, fallback to 60 if not found
        pixel_count = info.get('leds', {}).get('count', 60)
        name = info.get('name', None)
        
        # Universe will be automatically assigned based on IP
        manager.add_fixture(ip, pixel_count, name, info)
    
    return manager 


class SmartUniverseManager:
    def assign_universe(self, fixture) -> Tuple[int, int]:
        """
        Smart universe assignment:
        - Small fixtures (< 170 pixels) share universes
        - Large fixtures get their own universe
        """
        pixels = fixture.pixel_count
        channels = pixels * 3
        
        if channels <= 510:  # Leave room for padding
            # Try to fit in existing universe
            universe, start_channel = self._find_space_in_universes(channels)
            if universe is not None:
                return universe, start_channel
        
        # Assign new universe
        universe = self._get_next_universe()
        return universe, 0 