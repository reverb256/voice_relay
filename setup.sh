#!/bin/bash
# Voice Relay Setup Script
# Easy one-command setup for the voice relay system

set -e

echo "=== Voice Relay Setup ==="
echo ""

# Step 1: Install Python dependencies
echo "Installing Python dependencies..."
pip install flask plyer pystray pillow 2>&1 | tail -3

# Step 2: Create output directory
echo "Creating output directory..."
mkdir -p voice_messages

# Step 3: Start the server in background
echo "Starting voice relay server..."
nohup python3 simplified_server.py > /tmp/voice_relay_server.log 2>&1 &

# Wait for server to start
echo "Waiting for server to start..."
for i in $(seq 1 10); do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "Server is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "=== Voice Relay is running! ==="
echo ""
echo "Access points:"
echo "  Web interface: http://localhost:5000"
echo "  Health check:  curl http://localhost:5000/health"
echo "  Upload API:    curl -X POST -F 'audio=@message.oga' http://localhost:5000/upload"
echo "  Messages:      curl http://localhost:5000/messages"
echo ""
echo "Android PWA: Open http://localhost:5000 in your Android browser"
echo "  - Press & Hold to record voice message"
echo "  - Release button to send to Windows PC"
echo ""
echo "Windows: The server plays messages through VLC"
echo "  Messages appear in ./voice_messages/ directory"
echo ""
echo "To stop the server: pkill -f 'python3 simplified_server'"