# Voice Relay System

## Overview
A voice relay system where an Android device can record a voice message, release a button, and have it broadcast to a Windows PC through a web domain, with Tailscale networking and NSSM background service for speaker playback.

## Architecture
- **Flask Python server** (`simplified_server.py`) - Accepts OGG audio uploads from Android PWA, stores messages, serves playback, QR code generation, config persistence
- **Android PWA interface** - Press & hold to record, release to send, message list with playback
- **Windows playback** - VLC media player with NSSM background service
- **Tailscale networking** - Cross-device connectivity via Tailscale VPN
- **Config persistence** - `~/.voice_relay/config.yaml` with host/port, loads on subsequent runs

## Features
- ✅ Flask web server accepting voice message uploads from Android
- ✅ PWA interface for Android recording (press & hold to record, release to send)
- ✅ Message storage and retrieval system (polling-based for reliability)
- ✅ Windows playback via VLC media player
- ✅ System tray indicator with basic menu
- ✅ Two-way intercom capability (Windows can send messages back to Android)
- ✅ Tailscale networking awareness
- ✅ QR code generation and clipboard auto-copy on server startup
- ✅ Config persistence to `~/.voice_relay/config.yaml`
- ✅ Enhanced PWA interface with connection status, recording feedback, message list
- ✅ OGG/Opus audio format for mobile-friendly recordings
- ✅ One-command setup script (`setup.sh`)

## Repository Structure
```
voice_relay/
├── simplified_server.py          # Main Flask server with PWA interface
├── setup.sh                     # One-command setup script
├── voice_messages/              # Output directory for received voice messages
├── windows_service.py           # Windows service wrapper for NSSM
├── voice_relay_service.py       # Windows service management script
├── .gitignore                   # Python/git exclusions
├── AGENTS.md                    # Agent governance & git hygiene rules
├── LICENSE                      # MIT License
├── README.md                    # Project overview (this file)
└── .github/
    └── PULL_REQUEST_TEMPLATE.md # Standardized PR template
```

## Installation

### One-Command Setup
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# 1. Clone the repository
git clone https://github.com/reverb256/voice_relay.git
cd voice_relay

# 2. Install dependencies
pip install flask pyyaml qrcode pillow plyer pystray

# 3. Run the server
python3 simplified_server.py

# 4. Access the PWA interface
#    Open on Android: http://<server-ip>:5000
#    Or scan the QR code displayed on startup

# 5. For Windows background service
#    Install NSSM and use windows_service.py
```

### Tailscale Configuration
The server auto-detects Tailscale IP (`100.91.11.2` on this machine). 
- Ensure Tailscale is running on both Android and Windows
- Use the Tailscale IP for cross-device connectivity
- QR code on server startup shows the connection URL

### Windows NSSM Service
```bash
# Install NSSM and set up background service
python3 windows_service.py
# Follow the interactive prompts
```

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | PWA interface with QR code |
| `/health` | GET | Health check |
| `/upload` | POST | Upload voice message from Android |
| `/messages` | GET | List messages for recipient |
| `/message/<filename>` | GET | Play/retrieve a specific message |
| `/message/<filename>` | DELETE | Delete a message |

## Audio Format
- **Format**: OGG/Opus
- **Mobile-friendly**: Small file sizes, good quality
- **Storage**: `voice_messages/` directory
- **Playback**: VLC media player (Windows), any OGG-capable player

## Two-Way Intercom
- Android → Windows: Record and send voice messages
- Windows → Android: Send messages back via the same API
- Message polling ensures reliable delivery

## Configuration
- Saved to `~/.voice_relay/config.yaml`
- Contains: `host` and `port`
- Loads on subsequent server runs
- Auto-detects Tailscale IP (`100.91.11.2`)

## License
MIT License - see LICENSE file for details.

## Git Hygiene
Follow the rules in `AGENTS.md`:
- Never run `git add -A`, `git add .`, `git add --all`
- Never commit tool/session state files (.freebuff/, .sisyphus/, etc.)
- Stage explicit paths: `git add <path> [<path> ...]`