#!/bin/sh
set -e

PORT="${PORT:-8000}"

echo "Starting Robot Digital Twin on port ${PORT}..."
echo "PYTHONPATH=${PYTHONPATH:-/app}"

exec uvicorn src.api.server:app \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --proxy-headers \
  --forwarded-allow-ips="*"
