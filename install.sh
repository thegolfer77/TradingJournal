#!/usr/bin/env bash
set -euo pipefail

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  cd "$REPO_ROOT"
fi

if [ -f scripts/install.sh ]; then
  exec bash scripts/install.sh "$@"
fi

echo "[WARN] scripts/install.sh nicht gefunden – nutze lokalen Fallback"

if [ ! -f requirements.txt ]; then
  echo "[ERROR] requirements.txt fehlt im aktuellen Ordner: $(pwd)"
  echo "[HINWEIS] Prüfe Branch/Ordner oder klone neu:"
  echo "  cd ~ && rm -rf TradingJournal && git clone https://github.com/thegolfer77/TradingJournal.git"
  exit 1
fi

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[OK] Installation fertig"
