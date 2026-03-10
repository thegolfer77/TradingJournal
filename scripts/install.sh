#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-https://github.com/thegolfer77/TradingJournal.git}"
TARGET_DIR="${2:-TradingJournal}"
BRANCH="${3:-main}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[ERROR] '$1' ist nicht installiert."
    exit 1
  fi
}

require_cmd git
require_cmd python3

if [ -d "$TARGET_DIR/.git" ]; then
  echo "[INFO] Repository existiert bereits unter '$TARGET_DIR' – update wird ausgeführt"
  git -C "$TARGET_DIR" fetch --all --tags
else
  echo "[INFO] Klone $REPO_URL nach $TARGET_DIR"
  git clone "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"

if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH"
else
  echo "[WARN] Branch '$BRANCH' nicht gefunden, nutze aktuellen Branch: $(git rev-parse --abbrev-ref HEAD)"
fi

if [ ! -f requirements.txt ] || [ ! -d app ] || [ ! -f scripts/run.sh ]; then
  echo "[ERROR] Projektdateien fehlen (requirements.txt/app/scripts/run.sh)."
  echo "[HINWEIS] Prüfe Repo-URL und Branch."
  echo "[DEBUG] Aktueller Commit: $(git rev-parse --short HEAD)"
  exit 1
fi

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[OK] Installation fertig."
echo "[NEXT] Starten mit:"
echo "  cd $TARGET_DIR"
echo "  source .venv/bin/activate"
echo "  bash scripts/run.sh"
