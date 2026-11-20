#!/usr/bin/env python3
"""
Windows Service for Voice Relay via NSSM
========================================

Runs the Flask voice relay server as a background Windows service using NSSM.
Polls for new voice messages and plays them through the computer's speakers.

Installation:
    python windows_service.py --install
    # Then set up NSSM:
    nssm install VoiceRelay
    nssm set VoiceRelay Startup manual
    nssm start VoiceRelay

Control:
    python windows_service.py --start
    python windows_service.py --stop
    python windows_service.py --status
    python windows_service.py --uninstall
"""

import os
import sys
import argparse
import subprocess
import time
import signal
import logging
import threading
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from simplified_server import app, logger, OUTPUT_DIR

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Global state
service_running = True
flask_process = None


def start_flask_server():
    """Start the Flask server as a background process."""
    global flask_process
    
    host = os.environ.get("SERVER_HOST", "127.0.0.1")
    port = int(os.environ.get("SERVER_PORT", "5000"))
    
    logger(f"Starting Flask server on {host}:{port}")
    
    # Kill any existing Flask process on the same port
    try:
        result = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                pid = line.split()[-1]
                logger(f"Found existing process {pid} on port {port}, terminating")
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    except Exception:
        pass
    
    # Start Flask in background
    flask_process = subprocess.Popen(
        [sys.executable, str(project_dir / "simplified_server.py")],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    )
    
    # Wait for server to start
    import urllib.request
    import time
    max_wait = 10
    waited = 0
    
    while waited < max_wait:
        try:
            urllib.request.urlopen(f"http://{host}:{port}/health", timeout=2)
            logger(f"Flask server started successfully (PID: {flask_process.pid})")
            return True
        except Exception:
            time.sleep(0.5)
            waited += 0.5
    
    logger("Warning: Flask server may not have started properly")
    return False


def stop_flask_server():
    """Stop the Flask server process."""
    global service_running, flask_process
    service_running = False
    
    if flask_process and flask_process.poll() is None:
        logger("Stopping Flask server...")
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            flask_process.kill()
        flask_process = None
        logger("Flask server stopped")
    else:
        logger("Flask server already stopped")


def play_message(file_path):
    """Play a voice message through the computer's speakers."""
    if not os.path.exists(file_path):
        logger(f"Message file not found: {file_path}")
        return False
    
    logger(f"Playing message: {file_path}")
    
    try:
        # Try multiple audio players in order of preference
        players = [
            # VLC - play and exit
            ["vlc", "--play-and-exit", file_path],
            # mpg123 for MP3
            ["mpg123", "-q", file_path],
            # aplay for WAV (Linux), but try on Windows too
            ["powershell", "-Command", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"],
            # Windows default audio
            ["cmd", "/C", f"start /min "" ""{file_path}\""],
        ]
        
        played = False
        for player_cmd in players:
            try:
                subprocess.Popen(
                    player_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                )
                logger(f"Started playback with: {player_cmd[0]}")
                played = True
                break
            except Exception as e:
                logger.debug(f"Player {player_cmd[0]} failed: {e}")
                continue
        
        if not played:
            # Fallback: just log the file path
            logger(f"Message ready at {file_path} - no suitable player found")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Playback error: {e}")
        return False


def poll_messages(host, port, check_interval=3):
    """Poll the Flask server for new messages and play them."""
    import urllib.request
    import json
    
    logger(f"Starting message polling every {check_interval}s")
    
    last_message_check = 0
    
    while service_running:
        try:
            current_time = time.time()
            
            # Check for new messages at regular intervals
            if current_time - last_message_check >= check_interval:
                last_message_check = current_time
                
                try:
                    # Poll the messages endpoint
                    url = f"http://{host}:{port}/messages?recipient=default"
                    req = urllib.request.Request(url)
                    resp = urllib.request.urlopen(req, timeout=5)
                    
                    data = json.loads(resp.read().decode())
                    messages = data.get("messages", [])
                    
                    logger(f"Found {len(messages)} new message(s)")
                    
                    for msg in messages:
                        filename = msg.get("filename", "")
                        if filename:
                            # Get the file path from the server's message store
                            # We need to fetch the specific message
                            try:
                                msg_resp = urllib.request.urlopen(
                                    f"http://{host}:{port}/message/{filename}",
                                    timeout=5
                                )
                                msg_data = msg_resp.read().decode()
                                
                                # Save the file path info and play it
                                file_path = os.path.join(str(OUTPUT_DIR), f"{filename}.oga")
                                if os.path.exists(file_path):
                                    play_message(file_path)
                                    
                                    # Optionally remove played message
                                    # os.remove(file_path)
                                    
                            except Exception as e:
                                logger.debug(f"Failed to retrieve message {filename}: {e}")
                                
                except Exception as e:
                    logger.debug(f"Message poll request failed: {e}")
            
            # Sleep in small increments to allow checking service_running
            sleep_time = min(check_interval, 1.0)
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger("Received KeyboardInterrupt")
            break
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(check_interval)
    
    logger("Message polling stopped")


def run_service():
    """Main service entry point."""
    global service_running, flask_process
    
    logger("Voice Relay Service starting...")
    
    # Start Flask server
    if not start_flask_server():
        logger("Failed to start Flask server, exiting")
        return 1
    
    # Start message polling thread
    poll_thread = threading.Thread(
        target=poll_messages,
        args=("127.0.0.1", 5000),
        daemon=True
    )
    poll_thread.start()
    
    logger("Voice Relay Service running. Waiting for messages...")
    logger(""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Relay Windows Service")
    parser.add_argument("--install", action="store_true", help="Show NSSM installation instructions")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--stop", action="store_true", help="Stop the service")
    parser.add_argument("--status", action="store_true", help="Check service status")
    parser.add_argument("--uninstall", action="store_true", help="Show uninstall instructions")
    parser.add_argument("--port", type=int, default=5000, help="Flask server port")
    parser.add_argument("--host", default="127.0.0.1", help="Flask server host")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["SERVER_PORT"] = str(args.port)
    os.environ["SERVER_HOST"] = args.host
    
    if args.install:
        print("""NSSM Installation Instructions:

1. Download NSSM from: https://nssm.nssm.us/
2. Extract and add to your PATH
3. Run these commands:

   nssm install VoiceRelay
   nssm set VoiceRelay Application "C:\\Path\\To\\python.exe"
   nssm set VoiceRelay AppDirectory "C:\\Path\\To\\voice_relay\\directory"
   nssm set VoiceRelay Arguments "-u VoiceRelay service python windows_service.py --start"
   nssm set VoiceRelay Startup manual
   nssm install VoiceRelay
   nssm start VoiceRelay

4. To manage:
   nssm status VoiceRelay
   nssm stop VoiceRelay  
   nssm remove VoiceRelay
""")
        
    elif args.start:
        run_service()
        
    elif args.stop:
        stop_flask_server()
        
    elif args.status:
        if flask_process and flask_process.poll() is None:
            print("Voice Relay Service is RUNNING")
        else:
            print("Voice Relay Service is STOPPED")
            
    elif args.uninstall:
        print("""Uninstallation:
   nssm remove VoiceRelay
Or run: python windows_service.py
""")
        
    else:
        parser.print_help()