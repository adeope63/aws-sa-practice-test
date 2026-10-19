#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/runtime.sh
"$lab_python" -c 'import sys; assert sys.version_info >= (3, 12), "Python 3.12+ is required"'
"$lab_python" -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.lock.txt
cd frontend
if test -n "$lab_pnpm"; then
  "$lab_pnpm" install --frozen-lockfile
else
  npm install
fi
