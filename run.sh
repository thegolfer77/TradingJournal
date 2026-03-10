#!/usr/bin/env bash
set -euo pipefail

if [ -f scripts/run.sh ]; then
  exec bash scripts/run.sh "$@"
fi

echo "[WARN] scripts/run.sh nicht gefunden – starte direkt"
if [ ! -d .venv ]; then
  echo "[ERROR] .venv fehlt. Erst installieren: bash install.sh"
  exit 1
fi
. .venv/bin/activate
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
