#!/usr/bin/env bash
# Prefer normal installations; support the bundled Codex runtime on this device.
if ! command -v node >/dev/null 2>&1; then
  lab_node_bin="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
  if test -x "$lab_node_bin/node"; then export PATH="$lab_node_bin:$PATH"; fi
fi
if command -v python3.12 >/dev/null 2>&1; then
  lab_python=python3.12
elif test -x "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; then
  lab_python="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
else
  lab_python=python3
fi
if command -v pnpm >/dev/null 2>&1; then
  lab_pnpm=pnpm
elif test -x "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm"; then
  lab_pnpm="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm"
else
  lab_pnpm=''
fi
