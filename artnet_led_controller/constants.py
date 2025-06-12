"""
Constants and configuration for the WS2812B DMX Integration Library.
"""

# Network Configuration
DISCOVERY_PORT = 21324
ARTNET_PORT = 6454
DISCOVERY_PAYLOAD = b'{"op":"discover"}'

# Art-Net/DMX Configuration
MAX_PIXELS_PER_UNIVERSE = 170  # DMX512/Art-Net limit: 512 channels / 3 per RGB pixel
ARTNET_PROTOCOL_VERSION = 14    # Art-Net 4
ARTNET_OPCODE_DMX = 0x5000     # OpCode for ArtDMX packet

# Color Definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Default Configuration
DEFAULT_FPS = 30
DEFAULT_DISCOVERY_TIMEOUT = 2.0
DEFAULT_FIXTURE_PIXEL_COUNT = 60

# Logging Configuration
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S' 