#!/usr/bin/env bash
set -euo pipefail

if [ -f scripts/doctor.sh ]; then
  exec bash scripts/doctor.sh "$@"
fi

echo "[WARN] scripts/doctor.sh nicht gefunden – minimaler Fallback"
[ -f requirements.txt ] && echo "[OK] requirements.txt gefunden" || echo "[ERR] requirements.txt fehlt"
[ -d app ] && echo "[OK] app/ gefunden" || echo "[ERR] app/ fehlt"
[ -d .venv ] && echo "[OK] .venv vorhanden" || echo "[ERR] .venv fehlt"
