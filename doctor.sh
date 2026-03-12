#!/usr/bin/env bash
set -euo pipefail

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  cd "$REPO_ROOT"
fi

if [ -f scripts/doctor.sh ]; then
  exec bash scripts/doctor.sh "$@"
fi

echo "[WARN] scripts/doctor.sh nicht gefunden – minimaler Fallback"

echo "[INFO] Aktueller Ordner: $(pwd)"
[ -f requirements.txt ] && echo "[OK] requirements.txt gefunden" || echo "[ERR] requirements.txt fehlt"
[ -d app ] && echo "[OK] app/ gefunden" || echo "[ERR] app/ fehlt"
[ -d .venv ] && echo "[OK] .venv vorhanden" || echo "[ERR] .venv fehlt"
