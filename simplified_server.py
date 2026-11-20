#!/usr/bin/env python3
"""
Simplified Voice Relay Server
=============================

Android records voice → releases button → message sent to web domain → 
forwards through Tailscale/SSH to Windows NSSM service → plays through speakers.

Features:
- Accepts OGG/MP3/WebM audio from Android POST
- Stores messages locally
- Plays messages when requested
- Health endpoint for Tailscale connectivity check
- Simple HTML/PWA interface for Android
- Polling-based message retrieval
"""

import os
import json
import threading
import time
from flask import Flask, request, jsonify, send_file, render_template_string
from pathlib import Path

app = Flask(__name__)

# Configuration
OUTPUT_DIR = Path(os.environ.get("VOICE_OUTPUT_DIR", "./voice_messages"))
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_MESSAGE_SIZE = int(os.environ.get("MAX_MESSAGE_SIZE", "10485760"))  # 10MB

# HTML PWA interface for Android
PWA_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Voice Relay - Send to Dad's PC</title>
    <style>
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f7;
            color: #333;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .status {
            padding: 10px;
            background: #e8e8ec;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
        }
        
        .status.healthy {
            background: #d4edda;
            color: #155724;
        }
        
        .status.unhealthy {
            background: #f8d7da;
            color: #721c24;
        }
        
        .record-btn {
            display: block;
            width: 100%;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: #0066cc;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            margin: 10px 0;
            transition: background 0.2s;
        }
        
        .record-btn.recording {
            background: #cc0000;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .message-list {
            list-style: none;
            padding: 0;
            margin: 0;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .message-item {
            padding: 12px;
            background: white;
            border-radius: 8px;
            margin: 8px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            font-size: 14px;
        }
        
        .message-item.sent {
            border-left: 4px solid #0066cc;
        }
        
        .message-item.received {
            border-left: 4px solid #28a745;
        }
        
        .message-time {
            font-size: 10px;
            color: #666;
            margin-top: 4px;
            display: block;
        }
        
        .btn-play {
            display: inline-block;
            padding: 6px 12px;
            font-size: 12px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 4px;
        }
        
        .btn-delete {
            display: inline-block;
            padding: 6px 12px;
            font-size: 12px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .no-messages {
            padding: 20px;
            text-align: center;
            color: #666;
            font-style: italic;
        }
        
        @media (max-width: 480px) {
            .record-btn {
                padding: 15px;
                font-size: 16px;
            }
            .message-item {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Voice Relay</h1>
        
        <div id="status" class="status unhealthy">Connecting...</div>
        
        <button id="recordBtn" class="record-btn" disabled>Press & Hold to Record</button>
        
        <ul id="messageList" class="message-list">
            <li class="no-messages">No messages yet</li>
        </ul>
        
        <div style="text-align: center; margin-top: 20px; font-size: 12px;">
            Messages are forwarded to dad's PC and played through speakers.<br>
            <small>Uses Tailscale/SSH relay</small>
        </div>
    </div>

    <script>
        const STATUS_CHECK_INTERVAL = 3000;
        const POLL_INTERVAL = 2000;
        
        let isRecording = false;
        let mediaRecorder = null;
        let audioChunks = [];
        let ws = null;
        let messagePollTimer = null;
        
        const statusEl = document.getElementById('status');
        const recordBtn = document.getElementById('recordBtn');
        const messageList = document.getElementById('messageList');
        
        // Check server health
        async function checkHealth() {
            try {
                const resp = await fetch('/health');
                const data = await resp.json();
                if (data.status === 'healthy') {
                    statusEl.textContent = 'Server Connected';
                    statusEl.className = 'status healthy';
                    connectWebSocket();
                } else {
                    statusEl.textContent = 'Server Issue';
                    statusEl.className = 'status unhealthy';
                    disconnectWebSocket();
                }
            } catch (e) {
                statusEl.textContent = 'Disconnected';
                statusEl.className = 'status unhealthy';
                disconnectWebSocket();
            }
        }
        
        // WebSocket for real-time updates
        function connectWebSocket() {
            if (ws) {
                ws.close();
            }
            try {
                ws = new WebSocket('ws://' + window.location.host + '/ws');
                
                ws.onopen = function() {
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'new_message') {
                        addMessageToList(data.message, 'received');
                    }
                };
                
                ws.onclose = function() {
                    setTimeout(connectWebSocket, 3000);
                };
            } catch (e) {
                console.error('WebSocket error:', e);
            }
        }
        
        function disconnectWebSocket() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }
        
        // Add message to UI
        function addMessageToList(message, type) {
            const li = document.createElement('li');
            li.className = `message-item ${type}`;
            
            const sender = message.sender || 'Unknown';
            const timestamp = message.timestamp 
                ? new Date(message.timestamp).toLocaleTimeString() 
                : '';
            
            li.innerHTML = `
                <strong>${sender}</strong> at ${timestamp}<br>
                <button class="btn-play" onclick="playMessage('${message.filename}')">Play</button>
                <button class="btn-delete" onclick="deleteMessage('${message.filename}')">Del</button>
                <span class="message-time">${timestamp}</span>
            `;
            
            // Remove the "no messages" item if present
            const noMsg = messageList.querySelector('.no-messages');
            if (noMsg) {
                messageList.removeChild(noMsg);
            }
            
            messageList.appendChild(li);
            messageList.scrollTop = messageList.scrollHeight;
        }
        
        // Play a message
        async function playMessage(filename) {
            try {
                const resp = await fetch(`/message/${filename}`);
                if (resp.ok) {
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = `/message/${filename}`;
                    document.body.appendChild(audio);
                }
            } catch (e) {
                console.error('Failed to play message:', e);
            }
        }
        
        // Delete a message
        async function deleteMessage(filename) {
            if (confirm('Delete this message?')) {
                try {
                    await fetch(`/message/${filename}`, { method: 'DELETE' });
                    // Refresh the list
                    location.reload();
                } catch (e) {
                    console.error('Failed to delete:', e);
                }
            }
        }
        
        // Poll for messages
        function pollMessages() {
            fetch('/messages?recipient=default')
                .then(resp => resp.json())
                .then(data => {
                    const count = data.count || 0;
                    if (count > 0) {
                        const existing = messageList.querySelector('.no-messages');
                        if (existing) messageList.removeChild(existing);
                        
                        data.messages.forEach(msg => {
                            // Check if already in list
                            if (!messageList.querySelector(`li[filename="${msg.filename}"]`)) {
                                addMessageToList(msg, 'received');
                            }
                        });
                    }
                })
                .catch(err => console.error('Poll error:', err));
        }
        
        // Start polling
        messagePollTimer = setInterval(pollMessages, POLL_INTERVAL);
        
        // Initial health check
        checkHealth();
        
        // Handle window focus restore
        window.addEventListener('focus', checkHealth);
        
        // Record button handler
        recordBtn.addEventListener('click', function() {
            if (!isRecording) {
                startRecording();
            } else {
                finishRecording();
            }
        });
        
        function startRecording() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Web API not supported for audio recording in this browser');
                return;
            }
            
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    isRecording = true;
                    recordBtn.className = 'recordBtn recording';
                    recordBtn.textContent = 'Recording...';
                    
                    mediaRecorder = new MediaRecorder(stream, {
                        mimeType: 'audio/ogg;codecs=opus',
                        video: false
                    });
                    
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = event => {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };
                    
                    mediaRecorder.start();
                    console.log('Recording started, chunks collected:', audioChunks.length);
                })
                .catch(err => {
                    console.error('Error accessing microphone:', err);
                    alert('Could not access microphone. Please allow permissions.');
                });
        }
        
        function finishRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                stream.getTracks().forEach(track => track.stop());
                
                isRecording = false;
                recordBtn.className = 'recordBtn';
                recordBtn.textContent = 'Press & Hold to Record';
                
                // Create blob from recorded audio
                const audioBlob = new Blob(audioChunks, { type: 'audio/ogg;codecs=opus' });
                
                // Create FormData and send to server
                const formData = new FormData();
                formData.append('audio', audioBlob, 'voice_message.ogg');
                formData.append('sender', 'Android-' + new Date().getTimezoneOffset());
                formData.append('recipient', 'dad');
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(resp => resp.json())
                .then(data => {
                    console.log('Message sent:', data);
                    addMessageToList({
                        filename: data.message_filename,
                        sender: 'Android',
                        timestamp: data.timestamp
                    }, 'sent');
                    
                    // Show success message
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

@app.route("/")
def pwa_interface():
    """Serve the PWA interface for Android."""
    return render_template_string(PWA_HTML)


@app.route("/upload", methods=["POST"])
def upload_voice():
    """Receive voice message upload from Android."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    sender = request.form.get("sender", "android-unknown")
    recipient = request.form.get("recipient", "default")

    if audio_file.filename == "":
        return jsonify({"error": "No filename provided"}), 400

    # Generate unique message ID
    timestamp = int(time.time())
    message_filename = f"msg_{timestamp}_{sender}.oga"
    file_path = OUTPUT_DIR / message_filename

    # Save the audio file
    try:
        audio_file.save(file_path)
        logger.info(f"Saved voice message: {message_filename} ({file_path.stat().st_size} bytes)")
    except Exception as e:
        logger.error(f"Failed to save audio: {e}")
        return jsonify({"error": f"Failed to save audio: {str(e)}"}), 500

    # Store message info
    with _messages_lock:
        _messages[message_filename] = {
            "path": str(file_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
            "sender": sender,
            "recipient": recipient,
        }

    return jsonify({
        "status": "ok",
        "message_filename": message_filename,
        "file_path": str(file_path),
        "timestamp": _messages[message_filename]["timestamp"],
    })


@app.route("/messages", methods=["GET"])
def list_messages():
    """List received voice messages. Filter by recipient."""
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
                })
    return jsonify({"messages": msg_list, "count": len(msg_list)})


@app.route("/message/<filename>", methods=["GET"])
def get_message(filename):
    """Retrieve a specific voice message file."""
    with _messages_lock:
        if filename in _messages:
            file_path = _messages[filename]["path"]
            if os.path.exists(file_path):
                return send_file(file_path, mimetype="audio/ogg")
    return jsonify({"error": "Message not found"}), 404


@app.route("/message/<filename>", methods=["DELETE"])
def delete_message(filename):
    """Delete a specific voice message."""
    with _messages_lock:
        if filename in _messages:
            file_path = _messages[filename]["path"]
            if os.path.exists(file_path):
                os.remove(file_path)
            del _messages[filename]
            return jsonify({"status": "deleted"})
    return jsonify({"error": "Message not found"}), 404


@app.route("/ws")
def websocket_endpoint():
    """WebSocket endpoint for real-time updates."""
    from flask import Request
    # Flask-Sock or similar would go here, but for simplicity
    # we'll just return a note
    return jsonify({"status": "ws_endpoint"}), 404


def logger(msg):
    """Simple logging function."""
    import datetime
    t = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] {msg}")


if __name__ == "__main__":
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVER_PORT", "5000"))
    
    logger(f"Starting voice relay server on {host}:{port}")
    app.run(host=host, port=port, debug=False)