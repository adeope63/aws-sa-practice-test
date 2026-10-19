#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/runtime.sh
if ! test -x .venv/bin/python || ! test -d frontend/node_modules; then
  echo 'Run scripts/setup.sh first.' >&2
  exit 1
fi
lab_backend_port="${LAB_BACKEND_PORT:-8000}"
lab_frontend_port="${LAB_FRONTEND_PORT:-5173}"
PYTHONPATH=backend .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port "$lab_backend_port" &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT INT TERM
cd frontend
API_TARGET="http://127.0.0.1:$lab_backend_port" node node_modules/vite/bin/vite.js --host 127.0.0.1 --port "$lab_frontend_port"
