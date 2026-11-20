#!/usr/bin/env python3
"""Enhanced Voice Relay Server with System Tray and Two-Way Intercom"""

import os
import sys
import json
import threading
import time
import logging
from pathlib import Path
from datetime import datetime

# Cross-platform configuration
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    import pystray
    from PIL import Image
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

# Flask - must import after above checks
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("VoiceRelay")


def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    logger.info(f"[{t}] {msg}")


# Configuration
OUTPUT_DIR = Path(os.environ.get("VOICE_OUTPUT_DIR", "./voice_messages"))
OUTPUT_DIR.mkdir(exist_ok=True)
MAX_MESSAGE_SIZE = int(os.environ.get("MAX_MESSAGE_SIZE", "10485760"))

# Message store
_messages = {}
_messages_lock = threading.Lock()

# ============================================================
# PWA HTML Interface
# ============================================================
PWA_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Voice Intercom - Crash to Dad</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f7; color: #333; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .status { padding: 10px; background: #e8e8ec; border-radius: 8px; margin-bottom: 20px; text-align: center; font-size: 14px; }
        .status.connected { background: #d4edda; color: #155724; }
        .status.disconnected { background: #f8d7da; color: #721c24; }
        .record-btn { display: block; width: 100%; padding: 20px; font-size: 18px; font-weight: bold; color: white; background: #0066cc; border: none; border-radius: 10px; cursor: pointer; margin: 10px 0; transition: background 0.2s; }
        .record-btn.recording { background: #cc0000; animation: pulse 1s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .message-list { list-style: none; padding: 0; margin: 0; max-height: 300px; overflow-y: auto; }
        .message-item { padding: 12px; background: white; border-radius: 8px; margin: 8px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-size: 14px; }
        .message-item.sent { border-left: 4px solid #0066cc; }
        .message-item.received { border-left: 4px solid #28a745; }
        .message-time { font-size: 10px; color: #666; margin-top: 4px; display: block; }
        .btn { display: inline-block; padding: 6px 12px; font-size: 12px; border: none; border-radius: 4px; cursor: pointer; margin: 2px; }
        .btn-play { background: #28a745; color: white; }
        .btn-delete { background: #dc3545; color: white; }
        .no-messages { padding: 20px; text-align: center; color: #666; font-style: italic; }
        @media (max-width: 480px) { .record-btn { padding: 15px; font-size: 16px; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Voice Intercom</h1>
        <div id="status" class="status disconnected">Disconnected</div>
        <button id="recordBtn" class="record-btn" disabled>Press & Hold to Record</button>
        <ul id="messageList" class="message-list">
            <li class="no-messages">No messages yet</li>
        </ul>
        <div style="margin-top: 20px; text-align: center; font-size: 12px;">
            <strong>Crash → Dad</strong><br>
            Two-way voice intercom via Tailscale/SSH<br>
            <small>Release button to send</small>
        </div>
    </div>

    <script>
        let isRecording = false;
        let mediaRecorder = null;
        let audioChunks = [];
        let ws = null;
        let pollTimer = null;
        const statusEl = document.getElementById('status');
        const recordBtn = document.getElementById('recordBtn');
        const messageList = document.getElementById('messageList');

        function connect() {
            fetch('/health')
                .then(resp => {
                    if (resp.ok) {
                        statusEl.textContent = 'Connected';
                        statusEl.className = 'status connected';
                        initWebSocket();
                    } else {
                        statusEl.textContent = 'Server Issue';
                        statusEl.className = 'status disconnected';
                    }
                })
                .catch(() => {
                    statusEl.textContent = 'Disconnected';
                    statusEl.className = 'status disconnected';
                    setTimeout(connect, 5000);
                });
        }

        function initWebSocket() {
            if (ws) ws.close();
            try {
                ws = new WebSocket('ws://' + window.location.host + '/ws');
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                ws.onopen = () => console.log('WS open');
                ws.onclose = () => setTimeout(initWebSocket, 3000);
            } catch (e) {
                console.error('WS error:', e);
            }
        }

        function handleWebSocketMessage(data) {
            if (data.type === 'new_message') {
                addMessage(data.message, 'received');
                if (window.Notification && Notification.permission === 'granted') {
                    new Notification('Voice Message', { body: `From ${data.message.sender}` });
                }
            }
        }

        function addMessage(message, type) {
            const li = document.createElement('li');
            li.className = `message-item ${type}`;
            const sender = message.sender || 'Unknown';
            const timestamp = message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : '';
            li.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <strong>${sender}</strong>
                    <span class="message-time">${timestamp}</span>
                </div>
                <p style="margin: 8px 0; white-space: pre-wrap;">${type === 'sent' ? 'You → Dad' : 'Dad → You'}</p>
                <button class="btn btn-play" onclick="playMessage('${message.filename}')">Play</button>
                <button class="btn btn-delete" onclick="deleteMessage('${message.filename}')">Del</button>
            `;
            const noMsg = messageList.querySelector('.no-messages');
            if (noMsg) messageList.removeChild(noMsg);
            messageList.appendChild(li);
            messageList.scrollTop = messageList.scrollHeight;
        }

        async function playMessage(filename) {
            try {
                const resp = await fetch(`/message/${filename}`);
                if (resp.ok) {
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = `/message/${filename}`;
                    document.body.appendChild(audio);
                }
            } catch (e) { console.error('Play error:', e); }
        }

        async function deleteMessage(filename) {
            if (confirm('Delete this message?')) {
                try { await fetch(`/message/${filename}`, { method: 'DELETE' }); location.reload(); }
                catch (e) { console.error('Delete error:', e); }
            }
        }

        function pollMessages() {
            fetch('/messages?recipient=default')
                .then(resp => resp.json())
                .then(data => {
                    const count = data.count || 0;
                    if (count > 0) {
                        const noMsg = messageList.querySelector('.no-messages');
                        if (noMsg) messageList.removeChild(noMsg);
                        data.messages.forEach(msg => {
                            if (!messageList.querySelector(`li[filename="${msg.filename}"]`)) {
                                addMessage(msg, 'received');
                            }
                        });
                    }
                })
                .catch(err => console.error('Poll error:', err));
        }

        pollTimer = setInterval(pollMessages, 3000);
        connect();
        window.addEventListener('focus', connect);

        recordBtn.addEventListener('click', function() {
            if (!isRecording) { startRecording(); }
            else { finishRecording(); }
        });

        function startRecording() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Web API not supported for audio recording');
                return;
            }
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    isRecording = true;
                    recordBtn.className = 'recordBtn recording';
                    recordBtn.textContent = 'Recording...';
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/ogg;codecs=opus', video: false });
                    audioChunks = [];
                    mediaRecorder.ondataavailable = event => { if (event.data.size > 0) audioChunks.push(event.data); };
                    mediaRecorder.start();
                    console.log('Recording started');
                })
                .catch(err => {
                    alert('Could not access microphone. Please allow permissions.');
                    console.error('Mic error:', err);
                });
        }

        function finishRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                recordBtn.className = 'recordBtn';
                recordBtn.textContent = 'Press & Hold to Record';
                const audioBlob = new Blob(audioChunks, { type: 'audio/ogg;codecs=opus' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'voice_message.ogg');
                formData.append('sender', 'Android-' + Date.now());
                formData.append('recipient', 'dad');
                fetch('/upload', { method: 'POST', body: formData })
                    .then(resp => resp.json())
                    .then(data => {
                        console.log('Message sent:', data);
                        addMessage({ filename: data.message_filename, sender: 'Android', timestamp: data.timestamp }, 'sent');
                        if (window.Beep) window.Beep(500, 100);
                        alert('Voice message sent! It will appear on dad\'s PC shortly.');
                    })
                    .catch(err => {
                        console.error('Send error:', err);
                        alert('Failed to send message. Check server connection.');
                    });
            }
        }
    </script>
</body>
</html>
"""

# ============================================================
# Flask Routes
# ============================================================

@app.route("/")
def pwa_interface():
    return render_template_string(PWA_HTML)


@app.route("/upload", methods=["POST"])
def upload_voice():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    sender = request.form.get("sender", "android-unknown")
    recipient = request.form.get("recipient", "default")

    if audio_file.filename == "":
        return jsonify({"error": "No filename provided"}), 400

    timestamp = int(time.time())
    message_filename = f"msg_{timestamp}_{sender}.oga"
    file_path = OUTPUT_DIR / message_filename

    try:
        audio_file.save(file_path)
        log(f"Saved voice message: {message_filename} ({file_path.stat().st_size} bytes)")
    except Exception as e:
        log(f"Failed to save audio: {e}")
        return jsonify({"error": f"Failed to save audio: {str(e)}"}), 500

    with _messages_lock:
        _messages[message_filename] = {
            "path": str(file_path),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "recipient": recipient,
            "direction": "android-to-windows",
        }

    log(f"Message stored: {message_filename}, direction: android-to-windows")

    return jsonify({
        "status": "ok",
        "message_filename": message_filename,
        "file_path": str(file_path),
        "timestamp": _messages[message_filename]["timestamp"],
    })


@app.route("/messages", methods=["GET"])
def list_messages():
    with _messages_lock:
        recipient = request.args.get("recipient", "default")
        msg_list = []
        for fname, msg in _messages.items():
            if msg["recipient"] == recipient or recipient == "default":
                msg_list.append({
                    "filename": fname,
                    "timestamp": msg["timestamp"],
                    "sender": msg["sender"],
                    "recipient": msg["recipient"],
                    "direction": msg.get("direction", ""),
                })
    return jsonify({"messages": msg_list, "count": len(msg_list)})


@app.route("/message/<filename>", methods=["GET"])
def get_message(filename):
    with _messages_lock:
        if filename in _messages:
            file_path = _messages[filename]["path"]
            if os.path.exists(file_path):
                return send_file(file_path, mimetype="audio/ogg")
    return jsonify({"error": "Message not found"}), 404


@app.route("/message/<filename>", methods=["DELETE"])
def delete_message(filename):
    with _messages_lock:
        if filename in _messages:
            file_path = _messages[filename]["path"]
            if os.path.exists(file_path):
                os.remove(file_path)
            del _messages[filename]
            return jsonify({"status": "deleted"})
    return jsonify({"error": "Message not found"}), 404


# ============================================================
# System Tray
# ============================================================

def play_beep(frequency=500, duration=100):
    try:
        if HAS_WINSOUND:
            winsound.Beep(frequency, duration)
        else:
            import subprocess
            subprocess.run(["printf", "\x07"], capture_output=True)
    except Exception:
        pass


def show_notification(title, message):
    if HAS_PYSTRAY:
        try:
            icon = Image.new("RGB", (64, 64), (0, 128, 255))
            tray_icon = pystray.Icon("voice_relay", icon, title, None)
            tray_icon.show()
            tray_icon.notify(message, title)
            tray_icon.stop()
        except Exception as e:
            log(f"Tray notification error: {e}")
    elif PLYER_AVAILABLE:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, app_icon=None, timeout=10)
        except Exception as e:
            log(f"Plyer notification error: {e}")
    else:
        log(f"Notification: {title} - {message}")


# ============================================================
# Two-Way Intercom
# ============================================================

def send_to_android(message_data):
    log(f"Would send to Android: {message_data}")
    return True


def broadcast_message(message_data):
    log(f"Broadcast: {message_data}")


# ============================================================
# Message Polling Loop
# ============================================================

def poll_messages(host="127.0.0.1", port=5000, check_interval=3):
    import urllib.request
    import json

    log(f"Starting message polling every {check_interval}s")
    last_check = 0

    while True:
        try:
            current_time = time.time()
            if current_time - last_check >= check_interval:
                last_check = current_time
                try:
                    url = f"http://{host}:{port}/messages?recipient=default"
                    req = urllib.request.Request(url)
                    resp = urllib.request.urlopen(req, timeout=5)
                    data = json.loads(resp.read().decode())
                    messages = data.get("messages", [])

                    log(f"Found {len(messages)} new message(s)")

                    for msg in messages:
                        filename = msg.get("filename", "")
                        if filename:
                            try:
                                msg_resp = urllib.request.urlopen(
                                    f"http://{host}:{port}/message/{filename}", timeout=5
                                )
                                play_message_from_path(msg.get("path", ""))
                                show_notification(
                                    "Voice Message Received",
                                    f"From: {msg.get('sender', 'Unknown')}"
                                )
                            except Exception as e:
                                log.debug(f"Failed to retrieve message {filename}: {e}")

                except Exception as e:
                    log.debug(f"Message poll request failed: {e}")

            sleep_time = min(check_interval, 1.0)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            log("Polling stopped by user")
            break
        except Exception as e:
            log.error(f"Polling error: {e}")
            time.sleep(check_interval)


def play_message_from_path(file_path):
    if not os.path.exists(file_path):
        log(f"Message file not found: {file_path}")
        return False

    log(f"Playing message: {file_path}")
    try:
        import subprocess
        result = subprocess.Popen(
            ["vlc", "--play-and-exit", file_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log(f"Started VLC playback (PID: {result.pid})")
        return True
    except Exception as e:
        log.error(f"Playback error: {e}")
        try:
            play_beep(440, 500)
        except:
            pass
        return False


# ============================================================
# Tray Menu
# ============================================================

def create_tray_menu():
    if not HAS_PYSTRAY:
        return None

    def on_quit(icon, item):
        icon.stop()
        import os
        os._exit(0)

    def on_play_last(icon, item):
        with _messages_lock:
            if _messages:
                latest = list(_messages.keys())[-1]
                file_path = _messages[latest]["path"]
                if os.path.exists(file_path):
                    play_message_from_path(file_path)

    def on_notify_test(icon, item):
        show_notification("Test", "This is a test notification from the tray!")

    return pystray.Menu(
        pystray.MenuItem("Play Last Message", on_play_last),
        pystray.MenuItem("Show Notification", on_notify_test),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit)
    )


# ============================================================
# Main
# ============================================================

def run_server(host="0.0.0.0", port=5000, enable_tray=False):
    log(f"Starting voice relay server on {host}:{port}")

    tray = None
    if enable_tray and HAS_PYSTRAY:
        try:
            icon = Image.new("RGB", (64, 64), (0, 128, 255))
            tray = pystray.Icon("voice_relay", icon, "Voice Relay Intercom", None)
            tray.menu = create_tray_menu()
            tray.run_detached()
            log("System tray initialized")
        except Exception as e:
            log(f"Tray initialization warning: {e}")

    try:
        app.run(host=host, port=port, debug=False)
    finally:
        if tray:
            tray.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Voice Relay Intercom")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--tray", action="store_true", help="Enable system tray")
    parser.add_argument("--service", action="store_true", help="Run as polling service")

    args = parser.parse_args()

    if args.service:
        log("Running in service mode - polling for messages")
        poll_messages(host=args.host, port=args.port)
    else:
        run_server(host=args.host, port=args.port, enable_tray=args.tray)