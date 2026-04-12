#!/bin/bash

# Kill any existing process on port 5000
lsof -nP -iTCP:5000 -sTCP:LISTEN -t | xargs -r kill -9

# Start OpenClaw Gateway with explicit environment variable passing
# Using /bin/bash -l to ensure environment is loaded
cd /workspace/projects
/bin/bash -l -c 'export OPENCLAW_STATE_DIR=/workspace/projects && openclaw gateway run --port 5000 --allow-unconfigured --force' > /app/work/logs/bypass/dev.log 2>&1 &

# Wait and check if process started
sleep 5
if pgrep -f "openclaw-gateway" > /dev/null; then
    echo "✅ Gateway started successfully"
    echo "PID: $(pgrep -f 'openclaw-gateway')"
    echo ""
    echo "Checking connection..."
    sleep 2
    curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000 || echo "Note: May still be initializing"
else
    echo "❌ Failed to start Gateway. Check logs:"
    tail -n 30 /app/work/logs/bypass/dev.log
fi
