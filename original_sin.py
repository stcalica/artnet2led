"""
WS2812B DMX Integration Controller

---
PHYSICAL SETUP & NETWORKING CONTEXT
---
This script is designed for a setup where:
- A Raspberry Pi (running this script) is connected via Ethernet to a Power-over-Ethernet (PoE) switch.
- The PoE switch provides both data (Ethernet network) and power to an array of fixtures (e.g., WLED-based LED controllers) that support PoE and Art-Net/UDP control.

How this works in practice:
- **Raspberry Pi**: Acts as the controller, sending UDP packets (broadcast for discovery, unicast for control) over the wired network.
- **PoE Switch**: Forwards all Ethernet frames between devices. For broadcast packets (like device discovery), the switch sends the packet to all connected devices. For unicast packets (like Art-Net control to a specific fixture), it sends only to the target device.
- **Fixtures**: Each fixture is a network device with its own IP address, powered and networked via a single Ethernet cable. They listen for Art-Net packets and discovery messages.

**Networking Concepts:**
- **Ethernet Switch**: Unlike a hub, a switch learns which devices (MAC addresses) are on which ports and forwards unicast packets only to the correct port. Broadcast packets (like discovery) are sent to all ports.
- **PoE (Power over Ethernet)**: Allows both power and data to be delivered over the same cable, simplifying wiring for fixtures.
- **UDP Broadcast**: Used for device discovery. The Pi sends a packet to the broadcast address; the switch delivers it to all devices.
- **UDP Unicast**: Used for Art-Net control. The Pi sends a packet to a specific fixture's IP; the switch delivers it only to that device.

This setup is robust for lighting control because:
- Wired Ethernet is reliable and low-latency (important for real-time lighting effects).
- PoE reduces cabling complexity.
- The switch ensures efficient delivery of both broadcast and unicast packets.

---
LIMITATIONS, REQUIREMENTS, AND CONSIDERATIONS
---
1. This script is designed to control WS2812B (addressable RGB LED) fixtures using WLED firmware over a local network.
2. It uses UDP broadcast to discover WLED devices and sends Art-Net packets to control them.
3. The script assumes all WLED devices are on the same local network and are discoverable via UDP broadcast.
4. Only two patterns are implemented: 'chase' and 'strobe'.
5. The script does not handle more than 170 pixels per Art-Net universe (a DMX512/Art-Net limitation).
6. No error handling for network issues, device timeouts, or packet loss beyond basic socket timeouts.
7. Requires Python 3 and access to the 'socket', 'json', 'time', and 'struct' libraries (all standard in Python).
8. The script must be run on a machine connected to the same network as the WLED devices.
9. This script is for educational/demo purposes and is not production-hardened.
10. You may need to run as administrator/root to send broadcast packets, depending on your OS/network settings.

# --- DMX/Art-Net/Universe Explanation ---
# DMX512 is a protocol for lighting control that allows 512 channels per 'universe'.
# Each RGB LED pixel requires 3 channels (one for Red, one for Green, one for Blue).
# 512 / 3 = 170.666..., so you can control up to 170 RGB pixels per universe (510 channels used, 2 unused).
# Art-Net is a protocol for sending DMX data over Ethernet networks. Each Art-Net 'universe' is a separate DMX512 stream.
# If a fixture has more than 170 pixels, you must split its data across multiple universes (Art-Net packets),
# and the fixture must be configured to listen to those universes and map them to its pixel buffer.
# This script splits each fixture's data into 170-pixel chunks and sends each chunk as a separate Art-Net packet.
# The send_artnet() function should be updated to accept a universe parameter and use it in the Art-Net header for full support.
# WLED can be configured to listen to multiple universes and map them to its LEDs in the web UI.
# For more info, see: https://kno.wled.ge/interfaces/udp-realtime/#art-net
"""

# Import the socket library for network communication (UDP/TCP)
import socket
# Import json for encoding/decoding JSON data (used in WLED discovery)
import json
# Import time for delays and timeouts
import time
# Import struct for packing data into binary format (needed for Art-Net protocol)
import struct
import math
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock
import unittest

# --- LOGGING SETUP ---
# Set up logging to a file named with the current date for easy debugging and tracking.
# The log file will be named like 'ws2812b_dmx_YYYY-MM-DD.log'.
log_filename = f"ws2812b_dmx_{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# WLED discovery uses UDP broadcast on this port
DISCOVERY_PORT = 21324
# Art-Net protocol uses this port for sending DMX data
ARTNET_PORT = 6454
# The payload to send for WLED discovery (JSON format as bytes)
# This is NOT an Art-Net or DMX standard, but a WLED-specific convention.
# WLED (an open-source firmware for ESP8266/ESP32 LED controllers) implements its own UDP discovery protocol.
# The message '{"op":"discover"}' is what WLED devices expect for discovery on port 21324.
# When a WLED device receives this, it replies with a JSON packet containing its info (name, LED count, etc.).
# This is NOT understood by generic Art-Net or DMX devices—only by WLED firmware.
# Other protocols (like Art-Net) have their own discovery mechanisms, but this script is tailored for WLED.
# For more, see: https://kno.wled.ge/interfaces/udp-realtime/#wled-discovery
DISCOVERY_PAYLOAD = b'{"op":"discover"}'

# Pattern Config
PATTERN = "chase"  # Choose between "strobe" or "chase" patterns
FPS = 30  # Frames per second (how fast the animation updates)
FIXTURE_PIXEL_COUNT = 60  # Number of LEDs per fixture/tube
MAX_PIXELS_PER_UNIVERSE = 170  # Art-Net/DMX limitation (512 channels / 3 per pixel)

# Color definitions as RGB tuples
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAX_PIXELS_PER_UNIVERSE = 170  # DMX512/Art-Net limit: 512 channels / 3 per RGB pixel

# --- UTILITY FUNCTIONS ---
def log_error(message):
    """
    Log an error message to the log file and print to console for immediate feedback.
    """
    logging.error(message)
    print(f"[ERROR] {message}")

def log_info(message):
    """
    Log an informational message to the log file and print to console.
    """
    logging.info(message)
    print(f"[INFO] {message}")

# --- NETWORK DISCOVERY ---
def discover_wled(timeout=2):
    """
    Discover WLED fixtures on the local network using UDP broadcast.
    Returns a list of (IP, info_dict) for each discovered device.
    
    Concept: This function uses UDP broadcast to send a special message to the entire local network, asking all WLED devices to identify themselves. Each WLED device that receives this message replies with its information (including pixel count, name, etc.).
    ELI5: This function shouts out to the whole network, "Who is a WLED light?" and listens for replies.
    """
    discovered = []
    try:
        # --- SOCKET CREATION AND CONFIGURATION ---
        # Create a UDP socket. Sockets are endpoints for sending/receiving data across a network.
        # AF_INET: Address Family for IPv4 (most common for local networks)
        # SOCK_DGRAM: Datagram socket, which means UDP (connectionless, fast, but no delivery guarantee)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Enable broadcast mode on the socket. This allows sending packets to all devices on the subnet.
        # SO_BROADCAST: Socket option to allow sending to the special broadcast address (e.g., 192.168.1.255)
        # Why? WLED devices listen for discovery packets sent to the broadcast address, so this is required.
        # In your setup, the PoE switch will forward this broadcast packet to all connected fixtures.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Set a timeout (in seconds) for socket operations. This prevents the script from hanging forever if no devices respond.
        # Why? UDP is connectionless, so we need to decide how long to wait for replies.
        sock.settimeout(timeout)
        # --- SENDING DISCOVERY PACKET ---
        # Send the discovery payload (a JSON string as bytes) to the broadcast address on the discovery port.
        # '<broadcast>' is a special address that means 'send to all devices on the local network'.
        # DISCOVERY_PORT is the port WLED devices listen on for discovery messages (21324 by default).
        # Why? This is how we ask all WLED devices to identify themselves.
        # The PoE switch will ensure this packet reaches every fixture on the network.
        sock.sendto(DISCOVERY_PAYLOAD, ('<broadcast>', DISCOVERY_PORT))
        start = time.time()
        while time.time() - start < timeout:
            try:
                # Wait for a response from any device (up to 1024 bytes per packet)
                # This will block until data is received or the socket times out
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                # Parse the JSON response from the device. WLED replies with info about itself (name, LED count, etc.)
                info = json.loads(data.decode('utf-8'))
                discovered.append((ip, info))
            except socket.timeout:
                break
            except Exception as e:
                log_error(f"Error parsing discovery response: {e}")
                continue
    except Exception as e:
        log_error(f"Discovery failed: {e}")
    return discovered

# Function to send Art-Net DMX data to a WLED device
# ip: target device IP
# start_pixel: could be used for offsetting pixel data
# total_pixels: number of pixels to send data for
# data: list of RGB values (flattened)
# universe: the universe number for this data
def send_artnet(ip, total_pixels, data, universe):
    """
    Send Art-Net DMX data to a WLED fixture.
    Concept: Art-Net is a protocol for sending DMX512 lighting data over Ethernet networks. Each Art-Net packet contains a header (with protocol info, universe number, etc.) and a payload (the DMX channel data for up to 512 channels). Each fixture listens to a specific universe and updates its LEDs based on the DMX data in packets for that universe.
    ELI5: This function puts the color info for each LED into a special envelope (Art-Net packet) and sends it to the right light (by IP and universe).
    - ip: The IP address of the fixture.
    - total_pixels: Number of pixels to send data for.
    - data: List of RGB values (flattened).
    - universe: The Art-Net universe number for this fixture.
    # --- ART-NET PACKET STRUCTURE ---
    # An Art-Net packet is a binary message with a specific structure:
    #   - Header: Identifies the packet as Art-Net, specifies the operation (OpCode), protocol version, sequence, physical port, universe, and data length.
    #   - Payload: The DMX channel data (up to 512 bytes, one per channel).
    #
    # '>8sHHBBBBH' means:
    #   8s: 8-byte string ("Art-Net\0")
    #   H: unsigned short (OpCode)
    #   H: unsigned short (Protocol version)
    #   B: unsigned char (Sequence)
    #   B: unsigned char (Physical)
    #   B: unsigned char (Universe low byte)
    #   B: unsigned char (Universe high byte)
    #   H: unsigned short (Length of DMX data)
    #
    # Art-Net universe is a 16-bit number (0-32767) that identifies a specific DMX data stream.
    # The protocol splits this into two bytes for transmission:
    #   - universe_low: least significant 8 bits (0-255)
    #   - universe_high: most significant 8 bits (0-255)
    # When combined, (universe_high << 8) | universe_low gives the full universe number.
    # Fixtures are configured to listen to specific universes; only packets with matching universe numbers are used.
    # This allows you to control many fixtures or split large fixtures across multiple universes.
    # Example: If universe = 0x1234 (4660 decimal), universe_low = 0x34, universe_high = 0x12.
    #
    # Math explanation:
    #   - universe_low = universe & 0xFF: This masks out all but the lowest 8 bits (e.g., 0x1234 & 0xFF = 0x34)
    #   - universe_high = (universe >> 8) & 0xFF: This shifts right by 8 bits to get the high byte (e.g., 0x1234 >> 8 = 0x12)

    """

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        universe_low = universe & 0xFF  # e.g., 0x1234 & 0xFF = 0x34
        universe_high = (universe >> 8) & 0xFF  # e.g., (0x1234 >> 8) & 0xFF = 0x12
        packet_header = struct.pack(
            '>8sHHBBBBH',
            b'Art-Net\0',  # Protocol ID (must be exactly 'Art-Net\0')
            0x5000,        # OpCode for ArtDMX packet (0x5000 means DMX data)
            14,            # Protocol version (Art-Net 4 = 14)
            0, 0,          # Sequence, Physical (not used here)
            universe_low,  # Universe low byte (least significant 8 bits)
            universe_high, # Universe high byte (most significant 8 bits)
            total_pixels * 3  # Length of DMX data (3 bytes per pixel)
        )
        # The payload is the header plus the actual RGB data for the fixture's pixels.
        payload = packet_header + bytes(data)
        # Send the packet to the device's Art-Net port (UDP, unicast to the fixture's IP).
        sock.sendto(payload, (ip, ARTNET_PORT))
    except Exception as e:
        log_error(f"Failed to send Art-Net to fixture {ip} (universe {universe}, {total_pixels} pixels): {e}")

# Function to create a single-frame 'chase' pattern
# Only one pixel is lit at a time, moving along the strip
# length: total number of pixels
# step: which pixel is currently lit
# color: color of the lit pixel (default: WHITE)
def make_chase_frame(length, step, color=WHITE):
    """
    Create a single-frame 'chase' pattern.
    
    Concept: Only one pixel is lit at a time, moving along the strip like a running light. The lit pixel moves forward by one each frame, creating a chasing effect.
    ELI5: Imagine a row of lights where only one is on, and it moves down the line like a runner with a torch.
    - length: Total number of pixels.
    - step: Which pixel is currently lit.
    - color: Color of the lit pixel.
    """
    data = []  # List to hold RGB values for all pixels
    for i in range(length):
        # Math: step % length ensures the lit pixel wraps around to the start after reaching the end.
        if i == step % length:
            data.extend(color)
        else:
            data.extend(BLACK)
    return data

def make_strobe_frame(length, on):
    """
    Create a single-frame 'strobe' pattern.
    
    Concept: All pixels are either on (white - 255 255 255) or off (black - 000), toggling each frame. This creates a flashing effect.
    ELI5: Like turning all the lights on and off really fast, like a strobe light at a dance party.
    - length: Total number of pixels.
    - on: Boolean, True for all on, False for all off.
    """
    return list(WHITE * length) if on else list(BLACK * length)

# --- FIXTURE/UNIVERSE MAPPING ---
def assign_universes_to_fixtures(fixtures):
    """
    Assign each fixture its own universe, starting from 0 and incrementing.
    
    Concept: Each fixture gets a unique universe number (like a mailbox address) so the controller knows where to send its DMX data. This makes the system scalable and easy to expand.
    ELI5: Each light gets its own mailbox (universe number) so the controller knows where to send its messages.
    Returns a list of dicts: {ip, pixel_count, universe}
    """
    fixture_info = []
    for idx, (ip, info) in enumerate(fixtures):
        # Get pixel count from WLED discovery info, fallback to 60 if not found
        pixel_count = info.get('leds', {}).get('count', 60)
        fixture_info.append({'ip': ip, 'pixel_count': pixel_count, 'universe': idx})
    return fixture_info

# --- MAIN LOOP ---
def main():
    """
    Main control loop: discovers fixtures, assigns universes, generates patterns, and sends Art-Net data.
    
    Concept: This is the heart of the controller. It finds all the lights, gives each a universe (mailbox), generates the animation pattern, and sends the right data to each fixture in real time. If anything goes wrong, it logs the error with details.
    ELI5: Finds all lights, gives each a mailbox (universe), and keeps sending them color instructions in real time.
    """
    fixtures = discover_wled()
    if not fixtures:
        log_error("No WLED fixtures found on the network. Exiting.")
        return
    fixture_info = assign_universes_to_fixtures(fixtures)
    log_info(f"Found {len(fixture_info)} fixtures: {[f['ip'] for f in fixture_info]}")
    step = 0
    toggle = True
    delay = 1.0 / FPS  # Math: 1.0 / FPS gives the time in seconds between frames (e.g., 1/30 = 0.033s for 30 FPS)
    while True:
        try:
            # Calculate total pixels for all fixtures (for pattern generation)
            # Math: sum(f['pixel_count'] for f in fixture_info) adds up the pixel counts for all fixtures
            num_pixels = sum(f['pixel_count'] for f in fixture_info)
            if PATTERN == "chase":
                data = make_chase_frame(num_pixels, step)
            elif PATTERN == "strobe":
                data = make_strobe_frame(num_pixels, toggle)
                toggle = not toggle  # Math: toggles the strobe state (True/False) each frame
            else:
                data = [0] * (num_pixels * 3)  # Math: num_pixels * 3 gives the total number of RGB values needed
            # Send data to each fixture, each on its own universe
            pixel_offset = 0  # Tracks where each fixture's data starts in the full pattern
            for f in fixture_info:
                ip = f['ip']
                pixel_count = f['pixel_count']
                universe = f['universe']
                # Math: pixel_offset*3 is the starting index in the data list for this fixture's RGB data
                # Math: (pixel_offset+pixel_count)*3 is the ending index (not inclusive)
                fixture_data = data[pixel_offset*3:(pixel_offset+pixel_count)*3]
                send_artnet(ip, pixel_count, fixture_data, universe)
                pixel_offset += pixel_count  # Math: move the offset forward by this fixture's pixel count
            step += 1  # Math: advances the animation step for the next frame
            time.sleep(delay)  # Wait before sending the next frame
        except Exception as e:
            log_error(f"Main loop error: {e}")
            time.sleep(1)  # Wait a bit before retrying

# If this script is run directly (not imported), start the main function
if __name__ == "__main__":
    main()


