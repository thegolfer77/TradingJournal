#!/usr/bin/env bash
set -euo pipefail

ok() { echo "[OK] $1"; }
err() { echo "[ERR] $1"; }

[ -f requirements.txt ] && ok "requirements.txt gefunden" || err "requirements.txt fehlt"
[ -f Makefile ] && ok "Makefile gefunden" || err "Makefile fehlt"
[ -d app ] && ok "app/ gefunden" || err "app/ fehlt"

if command -v git >/dev/null 2>&1; then
  ok "git: $(git --version)"
else
  err "git fehlt"
fi

if command -v python3 >/dev/null 2>&1; then
  ok "python3: $(python3 --version)"
else
  err "python3 fehlt"
fi

if [ -d .venv ]; then
  ok ".venv vorhanden"
else
  err ".venv fehlt"
fi

echo "\nGit branch/commit:"
git rev-parse --abbrev-ref HEAD || true
git rev-parse --short HEAD || true
