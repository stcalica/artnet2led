"""
Art-Net packet generation and transmission module.

Handles the creation and sending of Art-Net DMX packets to WLED fixtures.
"""

import socket
import struct
import logging
from typing import List, Tuple
from .constants import (
    ARTNET_PORT, MAX_PIXELS_PER_UNIVERSE, ARTNET_PROTOCOL_VERSION, 
    ARTNET_OPCODE_DMX
)


class ArtNetSender:
    """
    Handles Art-Net packet generation and transmission to WLED fixtures.
    """
    
    def __init__(self):
        """Initialize the Art-Net sender."""
        self.logger = logging.getLogger(__name__)
        self._socket = None
    
    def _get_socket(self) -> socket.socket:
        """Get or create a UDP socket for Art-Net transmission."""
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self._socket
    
    def send_dmx_data(self, ip: str, universe: int, pixel_data: List[int]) -> bool:
        """
        Send DMX data to a specific fixture via Art-Net.
        
        Args:
            ip: Target fixture IP address
            universe: Art-Net universe number
            pixel_data: List of RGB values (flattened)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sock = self._get_socket()
            
            # Calculate universe bytes
            universe_low = universe & 0xFF
            universe_high = (universe >> 8) & 0xFF
            
            # Create Art-Net packet header
            packet_header = struct.pack(
                '>8sHHBBBBH',
                b'Art-Net\0',           # Protocol ID
                ARTNET_OPCODE_DMX,      # OpCode for DMX data
                ARTNET_PROTOCOL_VERSION, # Protocol version
                0, 0,                   # Sequence, Physical (unused)
                universe_low,           # Universe low byte
                universe_high,          # Universe high byte
                len(pixel_data)         # Length of DMX data
            )
            
            # Combine header and data
            payload = packet_header + bytes(pixel_data)
            
            # Send packet
            sock.sendto(payload, (ip, ARTNET_PORT))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Art-Net to {ip} (universe {universe}): {e}")
            return False
    
    def send_fixture_data(self, fixture, pixel_data: List[int]) -> bool:
        """
        Send pixel data to a specific fixture.
        
        Args:
            fixture: Fixture object with ip and universe
            pixel_data: List of RGB values for the fixture
            
        Returns:
            True if successful, False otherwise
        """
        return self.send_dmx_data(fixture.ip, fixture.universe, pixel_data)
    
    def send_multiple_fixtures(self, fixtures_data: List[Tuple]) -> bool:
        """
        Send data to multiple fixtures efficiently.
        
        Args:
            fixtures_data: List of (fixture, pixel_data) tuples
            
        Returns:
            True if all successful, False if any failed
        """
        success = True
        sock = self._get_socket()
        
        for fixture, pixel_data in fixtures_data:
            try:
                universe_low = fixture.universe & 0xFF
                universe_high = (fixture.universe >> 8) & 0xFF
                
                packet_header = struct.pack(
                    '>8sHHBBBBH',
                    b'Art-Net\0',
                    ARTNET_OPCODE_DMX,
                    ARTNET_PROTOCOL_VERSION,
                    0, 0,
                    universe_low,
                    universe_high,
                    len(pixel_data)
                )
                
                payload = packet_header + bytes(pixel_data)
                sock.sendto(payload, (fixture.ip, ARTNET_PORT))
                
            except Exception as e:
                self.logger.error(f"Failed to send to {fixture.ip}: {e}")
                success = False
        
        return success
    
    def close(self):
        """Close the socket connection."""
        if self._socket:
            self._socket.close()
            self._socket = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 