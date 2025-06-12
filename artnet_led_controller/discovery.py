"""
WLED device discovery module.

Handles UDP broadcast discovery of WLED fixtures on the local network.
"""

import socket
import json
import time
import logging
from typing import List, Tuple, Dict, Any
from .constants import DISCOVERY_PORT, DISCOVERY_PAYLOAD, DEFAULT_DISCOVERY_TIMEOUT


class WLEDDiscovery:
    """
    Handles discovery of WLED devices on the local network using UDP broadcast.
    
    This class encapsulates the discovery logic, making it reusable and testable.
    """
    
    def __init__(self, timeout: float = DEFAULT_DISCOVERY_TIMEOUT):
        """
        Initialize the WLED discovery service.
        
        Args:
            timeout: Timeout in seconds for discovery operations
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def discover_devices(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Discover WLED fixtures on the local network using UDP broadcast.
        
        Returns:
            List of (IP, info_dict) tuples for each discovered device.
            
        Raises:
            Exception: If discovery fails due to network issues
        """
        discovered = []
        
        try:
            # Create UDP socket for discovery
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(self.timeout)
            
            # Send discovery broadcast
            sock.sendto(DISCOVERY_PAYLOAD, ('<broadcast>', DISCOVERY_PORT))
            
            # Listen for responses
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    ip = addr[0]
                    info = json.loads(data.decode('utf-8'))
                    discovered.append((ip, info))
                    self.logger.info(f"Discovered WLED device at {ip}: {info.get('name', 'Unknown')}")
                except socket.timeout:
                    break
                except Exception as e:
                    self.logger.error(f"Error parsing discovery response: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Discovery failed: {e}")
            raise
            
        return discovered
    
    def discover_single_device(self, ip: str) -> Dict[str, Any]:
        """
        Attempt to discover a specific WLED device by IP.
        
        Args:
            ip: IP address of the device to discover
            
        Returns:
            Device info dictionary if found, None otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # Send discovery to specific IP
            sock.sendto(DISCOVERY_PAYLOAD, (ip, DISCOVERY_PORT))
            
            data, addr = sock.recvfrom(1024)
            if addr[0] == ip:
                info = json.loads(data.decode('utf-8'))
                self.logger.info(f"Discovered WLED device at {ip}: {info.get('name', 'Unknown')}")
                return info
                
        except Exception as e:
            self.logger.error(f"Failed to discover device at {ip}: {e}")
            
        return None 