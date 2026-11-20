#!/usr/bin/env python3
"""Windows service wrapper for the voice relay.
Runs as a background service via NSSM (Non-Sucking Service Manager).

This script:
1. Starts the Flask server in the background
2. Listens for voice message uploads from Android via Tailscale
3. Plays received messages when requested
4. Can be controlled via command-line arguments

Install as NSSM service:
    nssm install VoiceRelay
    nssm set VoiceRelay Startup manual
    nssm start VoiceRelay

Control commands:
    python voice_relay_service.py start
    python voice_relay_service.py stop
    python voice_relay_service.py status
"""

import os
import sys
import signal
import subprocess
import time
import argparse
import logging
from pathlib import Path

# Add the project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from server import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("voice_relay.log")
    ]
)
logger = logging.getLogger("VoiceRelayService")

# Global process references
flask_process = None
service_running = True


def start_flask():
    """Start the Flask server in a background thread."""
    global flask_process
    
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVER_PORT", "5000"))
    
    logger.info(f"Starting Flask server on {host}:{port}")
    
    # Run Flask in a separate thread
    import threading
    flask_thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False),
        daemon=True
    )
    flask_thread.start()
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Verify it's running
    import urllib.request
    try:
        urllib.request.urlopen(f"http://{host}:{port}/health", timeout=3)
        logger.info("Flask server is running and healthy")
        return True
    except Exception as e:
        logger.error(f"Flask server failed to start: {e}")
        return False


def stop_flask():
    """Stop the Flask server."""
    global service_running
    service_running = False
    logger.info("Shutting down Flask server...")
    # Flask daemon thread will be cleaned up on process exit


def handle_upload():
    """Check for new messages and process them."""
    # This is called periodically in the main loop
    pass


def play_message(message_path):
    """Play a received message using VLC or fallback to other methods."""
    import vlc
    
    logger.info(f"Playing message: {message_path}")
    
    try:
        instance = vlc.Instance()
        media = instance.media_new(message_path)
        player = instance.media_player_new()
        player.set_media(media)
        player.play()
        
        # Wait a bit for playback to start
        time.sleep(1)
        
        # Keep playing until done or stopped
        while service_running:
            state = player.get_state()
            if state in (vlc.State.Ended, vlc.State.Error):
                break
            time.sleep(0.5)
        
        return True
    except Exception as e:
        logger.error(f"Failed to play message: {e}")
        return False


def play_sound_fallback(sound_path):
    """Fallback sound playback using Windows APIs."""
    import ctypes
    try:
        # Windows Multimedia API
        user32 = ctypes.windll.user32
        result = user32.MessageBeep(user32.MB_ICONASTERISK)
        if result:
            logger.info("Played fallback system beep")
        return True
    except Exception as e:
        logger.error(f"Fallback sound failed: {e}")
        return False


def main_loop():
    """Main service loop."""
    global service_running, flask_process
    
    logger.info("Voice Relay Service starting...")
    
    # Start Flask server
    if not start_flask():
        logger.error("Failed to start Flask server, exiting")
        return 1
    
    logger.info("Voice Relay Service running. Waiting for messages...")
    
    # Main service loop
    check_interval = 2  # seconds between message checks
    
    while service_running:
        try:
            # Check for new messages (poll the messages endpoint)
            import urllib.request
            import json
            
            try:
                resp = urllib.request.urlopen(
                    "http://0.0.0.0:5000/messages?recipient=default-recipient",
                    timeout=5
                )
                messages_data = json.loads(resp.read().decode())
                
                # Process any new/unplayed messages
                for msg in messages_data:
                    msg_id = msg.get("id")
                    msg_path = msg.get("file_path", "")
                    
                    if msg_id and msg_path and os.path.exists(msg_path):
                        # Play the message
                        play_message(msg_path)
                        
                        # Optionally delete or mark as played
                        # os.remove(msg_path)
                        
            except Exception as e:
                logger.debug(f"Message check request: {e}")
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            logger.info("Received KeyboardInterrupt")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(check_interval)
    
    # Cleanup
    service_running = False
    logger.info("Voice Relay Service shutting down...")
    return 0


def install_service():
    """Instructions for installing as NSSM service."""
    print("""
To install this as a Windows service using NSSM:

1. Download NSSM from https://nssm.nssm.us/
2. Extract and add to PATH
3. Run these commands:

   nssm install VoiceRelay
   nssm set VoiceRelay Application "C:\\Path\\To\\python.exe"
   nssm set VoiceRelay AppDirectory "C:\\Path\\To\\voice_relay\\directory"
   nssm set VoiceRelay Arguments "-u VoiceRelay service python voice_relay_service.py"
   nssm set VoiceRelay Startup manual
   nssm install VoiceRelay
   nssm start VoiceRelay

4. To manage the service:
   nssm status VoiceRelay
   nssm stop VoiceRelay
   nssm remove VoiceRelay
""")


def uninstall_service():
    """Instructions for removing the NSSM service."""
    print("""
To remove the VoiceRelay service:

   nssm remove VoiceRelay

Or run this script with --uninstall flag.
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Relay Windows Service")
    parser.add_argument("action", nargs="?", choices=["start", "stop", "status", "install", "uninstall"],
                        help="Action to perform")
    parser.add_argument("--port", type=int, default=5000, help="Flask server port")
    parser.add_argument("--host", default="0.0.0.0", help="Flask server host")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["SERVER_PORT"] = str(args.port)
    os.environ["SERVER_HOST"] = args.host
    
    if args.action == "install":
        install_service()
    elif args.action == "uninstall":
        uninstall_service()
    elif args.action == "start":
        if flask_process is None or flask_process.poll() is not None:
            flask_process = subprocess.Popen(
                [sys.executable, str(project_dir / "server.py")],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"Started Flask process with PID {flask_process.pid}")
        else:
            logger.info("Flask server is already running")
        
        # Run the main loop
        sys.exit(main_loop())
    elif args.action == "stop":
        logger.info("Stopping service...")
        service_running = False
        if flask_process:
            flask_process.terminate()
            flask_process.wait()
        logger.info("Service stopped")
    elif args.action == "status":
        if flask_process and flask_process.poll() is None:
            print("Flask server is running")
        else:
            print("Flask server is not running")
    else:
        parser.print_help()
        print('''
Usage:
    python voice_relay_service.py start    # Start the service
    python voice_relay_service.py stop     # Stop the service
    python voice_relay_service.py status   # Check status
    python voice_relay_service.py install  # Install as NSSM service
    python voice_relay_service.py uninstall # Remove the service
''')