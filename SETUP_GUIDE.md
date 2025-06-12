# Art-Net LED Controller Setup Guide

## Quick Setup: Plug and Play

This guide will get your WLED fixtures working with the library in 3 simple steps.

## Step 1: Configure Each WLED Fixture (One Time Only)

For each WLED device, you need to set:

- **Static IP Address**
- **Art-Net Universe**

### How to Configure WLED:

1. **Connect to WLED WiFi** - Each WLED creates its own WiFi network
2. **Access web interface** - Go to `http://4.3.2.1` or `http://wled.local`
3. **Set Static IP**:
   - Go to **WiFi Settings**
   - Set **Static IP** to your desired address
   - Example: `192.168.1.100`
4. **Set Art-Net Universe**:
   - Go to **Sync Interfaces** → **UDP Realtime**
   - Set **Art-Net Universe** to match the last number of your IP
   - Example: IP `192.168.1.100` → Universe `100`
5. **Save and connect to your switch**

### Example Configuration:

| Fixture   | IP Address    | Universe | Notes             |
| --------- | ------------- | -------- | ----------------- |
| Fixture 1 | 192.168.1.100 | 100      | Living Room Left  |
| Fixture 2 | 192.168.1.101 | 101      | Living Room Right |
| Fixture 3 | 192.168.1.102 | 102      | Kitchen Counter   |
| Fixture 4 | 192.168.1.103 | 103      | Bedroom           |

## Step 2: Connect Everything

1. **Connect all WLED devices to your switch** via Ethernet
2. **Connect Raspberry Pi to the same switch**
3. **Power everything on**

## Step 3: Test and Use

### Test Discovery:

```bash
artnet-led-controller discover
```

You should see output like:

```
Found 4 fixtures:
  - Living Room Left at 192.168.1.100 (universe 100)
  - Living Room Right at 192.168.1.101 (universe 101)
  - Kitchen Counter at 192.168.1.102 (universe 102)
  - Bedroom at 192.168.1.103 (universe 103)
```

### Run Patterns:

```bash
# Red chase pattern
artnet-led-controller run chase --color red --duration 10

# Rainbow pattern
artnet-led-controller run rainbow --speed 1.0

# Turn off
artnet-led-controller off
```

## That's It!

Once configured, your fixtures will:

- ✅ Automatically be discovered
- ✅ Get the correct universe assignment
- ✅ Work with any pattern
- ✅ Be ready for automation

## Troubleshooting

### Fixtures Not Found?

1. Check all devices are on the same network
2. Verify static IPs are set correctly
3. Ensure Art-Net universes match IP numbers
4. Check Ethernet connections

### Wrong Colors/Patterns?

1. Verify Art-Net universe numbers match IP numbers
2. Check WLED is in Art-Net mode (not WLED protocol)
3. Ensure UDP Realtime is enabled in WLED

### Network Issues?

1. Use a dedicated network for lighting
2. Consider using VLANs to isolate traffic
3. Check switch supports the traffic volume

## Advanced: Custom IP Ranges

If you want to use different IP ranges:

| IP Range          | Universe Range | Example           |
| ----------------- | -------------- | ----------------- |
| 192.168.1.100-199 | 100-199        | Standard setup    |
| 10.0.0.10-99      | 10-99          | Alternative range |
| 172.16.1.1-50     | 1-50           | Small setup       |

Just make sure the **last octet of IP = universe number**.
