#!/bin/bash
# Launch the Robot Digital Twin (backend + frontend)

set -e
cd "$(dirname "$0")"

echo "=== Robot Digital Twin Launcher ==="

# Install Python deps if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    python3 -m pip install -r requirements.txt
fi

# Install frontend deps if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# Bootstrap RL model if missing (quick, non-blocking feel)
if [ ! -f "models/rl_smc_agent.pt" ]; then
    echo "No RL model found — bootstrapping (this may take ~2 min)..."
    python3 bootstrap_rl.py &
fi

echo ""
echo "Starting backend API on http://localhost:8000"
python3 run_digital_twin.py &
BACKEND_PID=$!

sleep 2

echo "Starting frontend on http://localhost:5173"
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "  Digital Twin is running!"
echo "  Frontend: http://localhost:8000  (recommended — all-in-one)"
echo "  Dev mode: http://localhost:5173  (requires both servers)"
echo ""
echo "  Presentation guide: see PRESENTATION.md"
echo "  Press Ctrl+C to stop"
echo "============================================"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
