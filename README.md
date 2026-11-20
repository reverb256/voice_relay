# Voice Relay Intercom

A voice message relay system where an Android device can record a voice message, release a button, and have it broadcast to a Windows PC through a web domain, with Tailscale networking and NSSM background service for speaker playback.

## 📋 Quick Overview

| Feature | Status |
|---------|--------|
| **Android PWA Interface** | ✅ Press & hold to record, release to send |
| **OGG/Opus Audio Format** | ✅ Mobile-friendly, small files |
| **Local Message Storage** | ✅ `voice_messages/` directory |
| **Two-way Intercom** | ✅ Windows can send messages back |
| **Tailscale Networking** | ✅ Secure cross-device connectivity |
| **NSSM Windows Service** | ✅ Background operation |
| **System Tray (Linux)** | ✅ Optional tray indicator |
| **QR Code Connection** | ✅ Scan to connect instantly |
| **Config Persistence** | ✅ `~/.voice_relay/config.yaml` |
| **Clipboard Auto-copy** | ✅ URL copied on startup |

## 📦 Installation

### Prerequisites

```bash
# Install dependencies
pip install flask qrcode pyyaml

# Optional: system tray (Linux)
pip install pystray pillow

# Optional: Windows service
# Install NSSM from https://nssm.nssm.us/
```

### Start the Server

```bash
# Basic startup (config saved to ~/.voice_relay/config.yaml)
python3 simplified_server.py

# With system tray (Linux only)
python3 simplified_server.py --tray

# Quick QR only (no server)
python3 simplified_server.py --test-qr --host 0.0.0.0 --port 5000
```

### Connect from Android

1. QR code appears automatically on first startup
2. Or URL is copied to clipboard
3. Open on Android browser
4. Grant microphone permission
5. "Press & Hold to Record" → release to send
6. Message appears on Windows PC; click Play to listen

### Windows Playback

- Messages stored in `voice_messages/` directory
- Play via VLC media player (recommended)
- Or click Play button in the PWA interface
- Messages can be deleted from the interface

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [`README.md`](README.md) | This file - quick start and overview |
| [`OMARCHY_2_AI_HELPERS_ROADMAP.md`](OMARCHY_2_AI_HELPERS_ROADMAP.md) | Omarchy 2 AI helpers future roadmap |
| [`OMARCHY_INTEGRATION_GUIDE.md`](OMARCHY_INTEGRATION_GUIDE.md) | Omarchy + Voice Relay integration details |
| [`setup.sh`](setup.sh) | One-command setup script |
| [`.gitignore`](.gitignore) | Git exclusions |
| [`LICENSE`](LICENSE) | Project license |

## 🌐 Tailscale Networking

For remote access over the internet:

1. Install Tailscale on both Android and Windows
2. Run `tailscale up` on both devices
3. Start the server: `python3 simplified_server.py`
4. QR code automatically shows Tailscale IP (`100.91.11.2` on this machine)
5. Messages travel through secure Tailscale mesh VPN

```bash
# Verify Tailscale connection
tailscale status

# Server auto-detects Tailscale IP
# No manual host configuration needed
```

## 🔧 Configuration

Server settings saved to `~/.voice_relay/config.yaml`:

```yaml
host: "0.0.0.0"  # Auto-detected, or Tailscale IP like "100.91.11.2"
port: 5000
```

On subsequent runs, config is loaded automatically. Change host/port with `--host` and `--port` flags.

## 🎯 Workflow Examples

### Local Use (Linux + Android + Windows)

```bash
# Start server on Linux Omarchy
python3 simplified_server.py  # QR appears, URL copied

# Throughout day:
# Android scans QR or opens http://100.91.11.2:5000
# Records messages → appear on Linux machine
# Click Play to listen through speakers

# Tailscale enables remote access anytime
```

### Remote Work (Windows + Android Away from Home)

```powershell
; On Windows PC:
python simplified_server.py  ; NSSM service keeps it running

; On Android (anywhere with internet):
1. Ensure Tailscale is running
2. Open browser to Tailscale URL
3. Record and send voice messages
4. Messages play through Windows speakers

; Benefits: works from anywhere, no port forwarding needed
```

### Development / Testing

```bash
# Quick test locally
python3 simplified_server.py --host 127.0.0.1 --port 5000

# Test QR generation
python3 simplified_server.py --test-qr

# Run endpoint tests
python3 -c "import sys; sys.path.insert(0, '.'); from simplified_server import app; ..."

# Full test suite
python3 tests/ -q  # if running CI
```

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" on Android | - Ensure server running<br>- Check host/port<br>- Try http://localhost:5000<br>- Verify Tailscale (`tailscale up`) |
| QR code not scanning | - Try manual URL entry<br>- Use `--test-qr` to verify<br>- Check camera permissions |
| No messages appearing | - Check `voice_messages/` exists<br>- Verify upload succeeded<br>- Poll `/messages` endpoint<br>- Check recipient filter |
| Audio won't play | - Ensure VLC installed<br>- Check OGG/Opus format<br>- Try different player<br>- Verify file permissions |
| Tailscale IP not showing | - Run `tailscale up` first<br>- Same network/cluster required<br>- Check firewall rules |
| Server crashes on startup | - Python 3.10+ required<br>- Install dependencies<br>- Review logs: `python3 simplified_server.py 2>&1` |

### Recovery

```bash
# Reset config to defaults
rm ~/.voice_relay/config.yaml
python3 simplified_server.py  # Re-generates

# Clear messages
rm -rf voice_messages/*

# Restart server
pkill -f simplified_server
python3 simplified_server.py
```

## 📁 Project Structure

```
voice_relay/
├── simplified_server.py    # Main Flask server (648 lines) - **UPDATED**
├── windows_service.py     # NSSM Windows service wrapper
├── setup.sh               # One-command setup script
├── README.md              # **Project overview & integration guide**
├── OMARCHY_2_AI_HELPERS_ROADMAP.md  # AI helpers future roadmap
├── OMARCHY_INTEGRATION_GUIDE.md   # Omarchy + voice relay integration
├── .gitignore             # Git exclusions - **UPDATED**
├── voice_messages/        # Output directory for received messages
├── voice_relay_service.py # Windows service helper
└── .git/                  # Git repository
```

## 📜 License

MIT License - free to use, modify, and distribute.

## 🤝 Related Projects

- **Omarchy 2**: Beautiful, modern Linux distribution ([omarchy.org](https://omarchy.org))
- **Tailscale**: Secure mesh VPN ([tailscale.com](https://tailscale.com))
- **NSSM**: Non-Sucking Service Manager ([nssm.nssm.us](https://nssm.nssm.us))
- **Flask**: Python web framework ([palletsprojects.com/p/flask/](https://palletsprojects.com/p/flask/))

## 💬 Getting Help

- **GitHub Issues**: Report bugs or feature requests at the GitHub repo
- **Documentation**: See individual doc files for detailed guides
- **Community**: Your existing Omarchy repos provide patterns and examples

---

*Voice Relay Intercom - Android to Windows voice message relay*
*Last updated: November 2026*