#!/bin/bash
# CHIKA Status

echo "🔍 CHIKA Status"
echo "==============="

# Backend
if [ -f /tmp/chika_backend.pid ] && ps -p $(cat /tmp/chika_backend.pid) > /dev/null 2>&1; then
    echo "✅ Backend: RUNNING"
    curl -s http://127.0.0.1:8000/health
else
    echo "❌ Backend: DOWN"
fi

# Tunnel
if ps aux | grep "cloudflared tunnel" | grep -v grep > /dev/null; then
    echo "✅ Tunnel: RUNNING"
    grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/chika_tunnel.log 2>/dev/null | head -1
else
    echo "❌ Tunnel: DOWN"
fi
