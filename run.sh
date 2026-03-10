#!/usr/bin/env bash
set -euo pipefail

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  cd "$REPO_ROOT"
fi

if [ -f scripts/run.sh ]; then
  exec bash scripts/run.sh "$@"
fi

echo "[WARN] scripts/run.sh nicht gefunden – starte direkt"

if [ ! -f requirements.txt ] || [ ! -d app ]; then
  echo "[ERROR] Projektdateien fehlen (requirements.txt/app) im Ordner: $(pwd)"
  echo "[HINWEIS] Nutze zuerst: bash install.sh"
  exit 1
fi

if [ ! -d .venv ]; then
  echo "[ERROR] .venv fehlt. Erst installieren: bash install.sh"
  exit 1
fi

. .venv/bin/activate
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
