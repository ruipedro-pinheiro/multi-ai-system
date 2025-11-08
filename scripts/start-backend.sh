#!/bin/bash
# CHIKA Backend Startup Script

BACKEND_DIR="/home/pedro/chika/backend"
VENV_PYTHON="$BACKEND_DIR/venv/bin/python"
MAIN_FILE="$BACKEND_DIR/main_simple.py"
LOG_FILE="/tmp/chika_backend.log"
PID_FILE="/tmp/chika_backend.pid"

# Kill existing
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    kill $OLD_PID 2>/dev/null
    sleep 2
fi

# Start
cd "$BACKEND_DIR"
nohup $VENV_PYTHON $MAIN_FILE > $LOG_FILE 2>&1 &
echo $! > $PID_FILE
echo "✅ Backend started (PID: $(cat $PID_FILE))"
sleep 3
curl -s http://127.0.0.1:8000/health
