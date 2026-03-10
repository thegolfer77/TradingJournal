#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-https://github.com/REPLACE_ME/TradingJournal.git}"
TARGET_DIR="${2:-TradingJournal}"

if ! command -v git >/dev/null 2>&1; then
  echo "[ERROR] git ist nicht installiert."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 ist nicht installiert."
  exit 1
fi

if [ -d "$TARGET_DIR/.git" ]; then
  echo "[INFO] Repository existiert bereits unter '$TARGET_DIR' – pull wird ausgeführt"
  git -C "$TARGET_DIR" pull
else
  echo "[INFO] Klone $REPO_URL nach $TARGET_DIR"
  git clone "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[OK] Installation fertig."
echo "[NEXT] Starten mit:"
echo "  cd $TARGET_DIR"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
