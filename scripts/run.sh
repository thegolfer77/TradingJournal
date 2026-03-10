#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
  echo "[ERROR] .venv fehlt. Bitte zuerst installieren: bash scripts/install.sh"
  exit 1
fi

if [ ! -d app ]; then
  echo "[ERROR] app/ fehlt. Bist du im Projektordner?"
  exit 1
fi

. .venv/bin/activate
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
