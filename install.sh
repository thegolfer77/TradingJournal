#!/usr/bin/env bash
set -euo pipefail

if [ -f scripts/install.sh ]; then
  exec bash scripts/install.sh "$@"
fi

echo "[WARN] scripts/install.sh nicht gefunden – nutze lokalen Fallback"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[OK] Installation fertig"
