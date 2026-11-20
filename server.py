#!/usr/bin/env python3
"""Voice relay server - receives voice messages from Android via web domain,
forwards them through Tailscale/SSH to a Windows NSSM service.

Usage:
    python server.py                # Run locally
    # Or deploy behind Tailscale/Ssh relay as described in README
"""

import os
import json
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import vlc  # For audio playback
import soundfile  # For audio processing

app = Flask(__name__)

# Configuration
OUTPUT_DIR = os.environ.get("VOICE_OUTPUT_DIR", "./received_messages")
MAX_MESSAGE_SIZE = int(os.environ.get("MAX_MESSAGE_SIZE", "10485760"))  # 10MB
STORE_MESSAGES = os.environ.get("STORE_MESSAGES", "true").lower() == "true"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Thread-safe message store
messages = {}  # id -> {path, timestamp, sender, etc.}
messages_lock = threading.Lock()


@app.route("/upload", methods=["POST"])
def upload_message():
    """Receive a voice message upload from Android.
    
    Expected form data:
    - audio: audio file (OGG, MP3, WAV, WebM)
    - sender: optional sender identifier (Android device name/ID)
    - recipient: optional recipient identifier (e.g., "dad", "computer-name")
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    sender = request.form.get("sender", "unknown-android")
    recipient = request.form.get("recipient", "default-recipient")

    if audio_file.filename == "":
        return jsonify({"error": "No filename provided"}), 400

    # Generate a unique ID for this message
    message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(audio_file)}"

    # Save the audio file
    file_path = os.path.join(OUTPUT_DIR, f"{message_id}.oga")
    audio_file.save(file_path)

    # Also convert to a more compatible format if needed
    try:
        import soundfile as sf
        data, samplerate = sf.read(file_path)
        # Convert to WAV for maximum compatibility
        wav_path = os.path.join(OUTPUT_DIR, f"{message_id}.wav")
        sf.write(wav_path, data, samplerate, format="WAV")
        # Remove the original if conversion succeeded
        os.remove(file_path)
        file_path = wav_path
    except Exception:
        # If conversion fails, keep the original
        pass

    # Store message info
    with messages_lock:
        messages[message_id] = {
            "path": file_path,
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "recipient": recipient,
            "size": os.path.getsize(file_path),
        }

    app.logger.info(
        f"Received message {message_id} from {sender} for {recipient}, "
        f"size={os.path.getsize(file_path)}"
    )

    return jsonify({
        "status": "ok",
        "message_id": message_id,
        "file_path": file_path,
    })


@app.route("/messages", methods=["GET"])
def list_messages():
    """List received messages. Filter by recipient if desired."""
    with messages_lock:
        msg_list = []
        for mid, msg in messages.items():
            if msg["recipient"] == request.args.get("recipient", "default-recipient") or \
               not request.args.get("recipient"):
                msg_list.append({
                    "id": mid,
                    "timestamp": msg["timestamp"],
                    "sender": msg["sender"],
                    "recipient": msg["recipient"],
                    "size": msg["size"],
                })
    return jsonify(msg_list)


@app.route("/message/<message_id>", methods=["GET"])
def get_message(message_id):
    """Retrieve a specific message by ID."""
    with messages_lock:
        if message_id in messages:
            msg = messages[message_id]
            return send_file(msg["path"], mimetype="audio/wav")
    return jsonify({"error": "Message not found"}), 404


@app.route("/play/<message_id>", methods=["POST"])
def play_message(message_id):
    """Request playback of a message (for the Windows service to use)."""
    with messages_lock:
        if message_id not in messages:
            return jsonify({"error": "Message not found"}), 404

        msg = messages[message_id]

    try:
        import vlc
        player = vlc.Instance()
        mediaplay = player.media_new(msg["path"])
        player.media_player_play(mediaplay)

        # Wait for playback to start (simple approach)
        import time
        time.sleep(0.5)

        return jsonify({
            "status": "playing",
            "message_id": message_id,
            "file": msg["path"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVER_PORT", "5000"))
    debug = os.environ.get("SERVER_DEBUG", "false").lower() == "true"

    app.logger.info(f"Starting voice relay server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)