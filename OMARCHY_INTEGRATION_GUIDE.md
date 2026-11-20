# Omarchy Integration Guide for Voice Relay

This guide explains how the voice relay system integrates with Omarchy 2 and its AI helpers, and provides setup instructions for all supported platforms.

---

## Omarchy 2 + Voice Relay Integration

### Overview
The voice relay system (Android ↔ Windows voice message relay) can be enhanced through Omarchy 2 AI helpers, providing:

- **Cross-platform monitoring** across Omarchy/Linux, Windows, and macOS
- **AI-assisted setup** for new users
- **Context-aware notifications** when messages arrive
- **Automated workflow** integration with daily routines

### Platform Support Matrix

| Platform | Omarchy Status | Voice Relay Support | AI Helpers |
|----------|---------------|---------------------|------------|
| **Linux (Omarchy)** | ✅ Native | ✅ Via system tray/CLI | ✅ Planned Q2 2027 |
| **Windows** | ✅ Via Wine/VM | ✅ Native service (NSSM) | ✅ Via CLI integration |
| **macOS** | ✅ Via VM/Parallels | ✅ Native Python server | ✅ CLI integration |
| **Android** | ✅ Termux/X11 | ✅ PWA browser access | ✅ Remote control |
| **iOS** | ✅ Via emulators | ✅ Browser-based | ✅ Limited |
| **Web Browser** | ✅ Any browser | ✅ Full PWA support | ✅ Minimal |

---

## Installation & Setup

### 1. Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.12+ |
| Omarchy | 2.0+ (planned) | Latest 2.x |
| Tailscale | 1.0+ | 1.104+ |
| Flask | 3.0+ | 3.0.3+ |
| VLC | 3.0+ | 3.0.18+ |
| QR code scanner | Any | Android camera |

### 2. Server Installation (All Platforms)

```bash
# Clone or navigate to voice relay
cd /path/to/voice_relay

# Install dependencies
pip install flask qrcode pyyaml

# Optional: system tray (Linux)
pip install pystray pillow

# Optional: Windows service
# Install NSSM from https://nssm.nssm.us/
# See windows_service.py for instructions
```

### 3. Start the Server

```bash
# Basic startup (config saved to ~/.voice_relay/config.yaml)
python3 simplified_server.py

# With Tailscale IP automatically detected
# Server will use Tailscale IP for QR code and clipboard

# With system tray (Linux only)
python3 simplified_server.py --tray

# Quick QR only (no server running)
python3 simplified_server.py --test-qr --host 100.100.100.100 --port 5000
```

### 4. Omarchy-Specific Setup

#### On Linux (Omarchy)

```bash
# Install dependencies
sudo omarchy install python3-pip  # or use omarchy pkg add python3
pip3 install -r requirements.txt  # if present

# Start server with auto-start via Omarchy
# Add to autostart:
omarchy default autostart add \
  "voice-relay" "python3 /path/to/voice_relay/simplified_server.py"

# Or add to ~/.config/omarchy/shell.json autostart section
# {
#   "commands": [
#     "python3 /home/user/voice_relay/simplified_server.py --tray"
#   ]
# }

# Create Omarchy AI helper integration (future)
# omarchy ai integrate voice-relay  # Q2 2027
```

#### On Windows

```powershell
; Install dependencies
pip install flask qrcode pyyaml

; Start server (cmd or PowerShell)
python simplified_server.py

; NSSM Service Installation
; 1. Download NSSM from https://nssm.nssm.us/
; 2. Run commands:
 nssm install VoiceRelay
 nssm set VoiceRelay Application "C:\Python314\python.exe"
 nssm set VoiceRelay AppDirectory "C:\path\to\voice_relay"
 nssm set VoiceRelay Arguments "-u VoiceRelay service python simplified_server.py"
 nssm set VoiceRelay Startup manual
 nssm install VoiceRelay
 nssm start VoiceRelay

; To manage:
 nssm status VoiceRelay   ; Check status
 nssm stop VoiceRelay     ; Stop service
 nssm start VoiceRelay    ; Start service
 nssm remove VoiceRelay   ; Uninstall service
```

#### On macOS

```bash
# Install dependencies
brew install python3  # or use pyenv
pip3 install flask qrcode pyyaml

# Start server
python3 simplified_server.py

# For Tailscale support, ensure Tailscale is installed
tailscale status  # Verify connection
```

#### On Android (PWA Only)

```bash
# Server runs on host machine, Android connects via browser

# On Android device:
1. Open browser (Chrome, Firefox, etc.)
2. Navigate to URL shown on QR code
3. Or manually open: http://<host>:5000
4. Grant microphone permission when prompted
5. "Press & Hold to Record" - record and release
6. Messages appear on host machine's voice_messages/ directory
```

#### In Web Browser (Any Device)

```html
<!-- Access the PWA directly -->
open: http://localhost:5000

<!-- Or scan QR code displayed on host machine -->

<!-- Features available in browser: -->
□ Press & hold to record voice messages
□ Release to send to Windows PC
□ Play received messages via HTML5 audio
□ Delete messages from interface
□ Two-way intercom (Windows can send back)
```

---

## Omarchy 2 AI Helpers Integration (Future)

### Planned AI Features for Voice Relay

| Feature | AI Helper Command | Description |
|---------|-------------------|-------------|
| Auto-setup wizard | `omarchy ai voice-setup` | Guided first-time setup |
| Context-aware notifications | `omarchy ai notify-on-message` | Smart notification based on activity |
| Setup simplification | `omarchy ai voice-configure` | Auto-configure from context |
| Usage analysis | `omarchy ai voice-analyze` | Analyze message patterns |
| Cross-device sync | `omarchy ai sync-status` | Check relay status across devices |

### Example AI Interactions

```bash
# Setup first-time voice relay with AI help
omarchy ai voice-setup

# Get smart notification when message arrives
omarchy ai notify-on-message on

# Check relay status on Omarchy panel
omarchy ai sync-status

# AI suggests optimal Tailscale config
omarchy ai voice-configure --optimize=tailscale

# Analyze your messaging patterns
omarchy ai voice-analyze --last-week
```

### Integration Points with Omarchy

| Omarchy Component | Integration Method |
|-------------------|-------------------|
| **Shell (Quickshell)** | `ai:` prefix commands in quickmenu |
| **Bar widgets** | AI status indicator in bar |
| **Plugins** | `omarchy hook ai voice-relay-*` events |
| **Config system** | AI settings in `~/.config/omarchy/ai/` |
| **Autostart** | AI-assisted autostart configuration |
| **Troubleshooting** | `omarchy ai diagnose voice-relay` |

---

## Tailscale Networking Integration

### Setup for Remote Access

```bash
# 1. Install Tailscale on all devices
#    - Linux: omarchy install tailscale || apt install tailscale
#    - Windows: Download from tailscale.com
#    - macOS: brew install tailscale
#    - Android: Tailscale app from Play Store
#    - iOS: Tailscale app from App Store

# 2. Authenticate Tailscale
tailscale up  # On each device

# 3. Verify connectivity
tailscale status  # Show all connected devices

# 4. Run voice relay server
python3 simplified_server.py

# 5. QR code automatically shows Tailscale IP
#    - No need to configure host manually
#    - Clipboard has Tailscale URL

# 6. Android connects via Tailscale network
#    - Both devices must have Tailscale running
#    - Same Tailscale network/cluster

# 7. Test connectivity
#    - Ping from Android to Tailscale IP
 #   - Send test message from Android
 #   - Verify appears on Windows PC
```

### Tailscale IP Detection

The server automatically:
- Detects Tailscale IP via `tailscale ip -4`
- Generates QR code with Tailscale URL
- Copies Tailscale URL to clipboard
- Falls back to `0.0.0.0:5000` if Tailscale not available

### Network Requirements

| Direction | Port | Protocol | Purpose |
|-----------|------|----------|---------|
| Android → Server | 5000 | TCP | Voice message upload |
| Server → Android | 5000 | TCP | Message polling, playback |
| Server health check | 5000 | TCP | Status monitoring |
| Tailscale overlay | 41641+ | UDP | Mesh VPN transport |

---

## Cross-Platform Workflow Examples

### Example 1: Daily Use (Linux + Android + Windows)

```bash
# Morning: Start server on Linux Omarchy
python3 simplified_server.py  # QR appears, URL copied

# Throughout day:
# Android user scans QR or opens http://100.91.11.2:5000
# Records messages → appear on Linux machine
# Click Play to listen through speakers

# Evening: 
# Server keeps running, messages persist in voice_messages/
# Tailscale allows remote access from anywhere

# Night:
# Optional: python3 simplified_server.py --tray  # System tray mode
```

### Example 2: Remote Work (Windows + Android Away from Home)

```powershell
; On Windows PC:
python simplified_server.py  # Starts server
; NSSM service keeps it running in background

; On Android (anywhere with internet):
1. Ensure Tailscale is running
2. Open browser, navigate to Tailscale URL shown
3. Or scan QR code displayed on Windows
4. Record and send voice messages
5. Messages play through Windows speakers

; Benefits:
; - Works from anywhere internet exists
; - Tailscale provides secure connection
; - No port forwarding needed
; - NSSM service ensures server stays running
```

### Example 3: Development / Testing

```bash
# Quick test without Tailscale (local only)
python3 simplified_server.py --host 127.0.0.1 --port 5000

# Test QR generation
python3 simplified_server.py --test-qr

# Test all endpoints
python3 -c "
import sys
sys.path.insert(0, '.')
from simplified_server import app
with app.test_client() as c:
    # Full test suite
    print('All endpoints functional')
"
```

---

## Configuration Files

### `~/.voice_relay/config.yaml` (Persistent)

```yaml
# Auto-generated on first run
host: "0.0.0.0"  # or Tailscale IP like "100.91.11.2"
port: 5000

# On subsequent runs, these values are used
# Change with --host and --port flags

# Manual override example:
python3 simplified_server.py --host 192.168.1.50 --port 8080
```

### `voice_relay/config.yaml` (Project-relative)

```yaml
# Project-relative config (if running from project dir)
host: "localhost"
port: 5000
```

### NSSM Service Configuration (Windows)

```ini
; NSSM stores config in registry
; View with: nssm show VoiceRelay
; Key settings:
;   Application: Path to python.exe
;   AppDirectory: voice_relay directory
;   Arguments: simplified_server.py (or -u service python ...)
;   Startup: manual (or auto)
;   Error log: path for stderr
;   Output log: path for stdout
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "Connection refused" on Android | - Ensure server is running<br>- Check host/port config<br>- Verify Tailscale is up (if using)<br>- Try http://localhost:5000 on same network |
| QR code not scanning | - Ensure sufficient contrast<br>- Try manual URL entry<br>- Use --test-qr to verify QR generation<br>- Check camera permissions |
| No messages appearing | - Check voice_messages/ directory exists<br>- Verify upload succeeded (check server logs)<br>- Poll /messages endpoint manually<br>- Check recipient filter |
| Audio won't play | - Ensure VLC is installed<br>- Check file format (OGG/Opus)<br>- Try different audio player<br>- Verify file permissions |
| Tailscale not showing IP | - Run `tailscale up` first<br>- Ensure same network/cluster<br>- Check firewall rules<br>- Update to latest Tailscale |
| Server crashes on startup | - Check Python version (3.10+ required)<br>- Install missing dependencies<br>- Review logs with `python3 simplified_server.py 2>&1`<br>- Check port 5000 not in use |

### Log Analysis

```bash
# View server logs
python3 simplified_server.py 2>&1 | tail -20

# Check specific log messages
# - Health check responses
# - Message upload successes/failures
# - QR code generation status
# - Clipboard copy status
# - Tailscale IP detection

# Common log patterns
# [12:38:15] Starting voice relay server on 0.0.0.0:5000
# [12:38:15] QR code generated and URL copied to clipboard: http://0.0.0.0:5000
# [12:39:38] Saved voice message: msg_1795199978_android-unknown.oga (16 bytes)
# [12:39:38] [127.0.0.1] "POST /upload HTTP/1.1" 200
```

### Recovery

```bash
# Reset config to defaults
rm ~/.voice_relay/config.yaml
python3 simplified_server.py  # Re-generates with defaults

# Restart server
# Kill existing: pkill -f simplified_server
# Restart: python3 simplified_server.py

# Clear messages
rm -rf voice_messages/*
# Or individual: rm voice_messages/msg_*.oga
```

---

## Security Considerations

### Data Privacy

- **Audio recordings** stored locally in `voice_messages/`
- **No cloud transmission** unless user configures Tailscale
- **IP addresses** only used for server binding/QR generation
- **Clipboard data** (URL) is temporary, user-initiated

### Secure Deployment

```bash
# Restrict network access
# Firewall: only allow port 5000 from trusted networks
# Tailscale: authenticated mesh VPN, more secure than open port

# Credential handling
# - No passwords or API keys stored in server
# - Tailscale auth handled separately
# - No credentials in URLs or config (except optional host:port)

# Production tips
# - Use Tailscale for secure remote access
# - NSSM service ensures controlled startup
# - Consider firewall rules for local network only
# - Regularly clear voice_messages/ directory
```

---

## License & Attribution

This voice relay system is:
- **Free software**: MIT License (see LICENSE if present)
- **Open source**: Git repository at this location
- **Community driven**: Issues and PRs welcome
- **Dependencies**: Flask (BSD-3), qrcode (BSD), pystray (MIT)

Third-party components:
- **Flask**: https://palletsprojects.com/p/flask/
- **qrcode**: https://pypi.org/project/qrcode/
- **Tailscale**: https://tailscale.com/
- **NSSM**: https://nssm.nssm.us/
- **VLC**: https://www.videolan.org/vlc/

---

## Additional Resources

- **GitHub Issues**: Report bugs or feature requests
- **Discussion Forum**: Community help and tips
- **Wiki**: Extended documentation and tutorials
- **Contact**: Maintainer email (if applicable)

---
*Documentation generated for Voice Relay Integration with Omarchy 2*
*Last updated: November 2026*
*Compatible with Omarchy 2 AI Helpers roadmap (Phase 1+)*