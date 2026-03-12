#!/usr/bin/env bash
set -euo pipefail

# Works even when install.sh/run.sh/requirements.txt are missing in current checkout.

if ! command -v git >/dev/null 2>&1; then
  echo "[ERR] git fehlt"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[ERR] Kein Git-Repository. Erst klonen:"
  echo "  git clone https://github.com/thegolfer77/TradingJournal.git"
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

echo "[INFO] Repo root: $ROOT"
echo "[INFO] Aktueller Branch: $(git rev-parse --abbrev-ref HEAD)"

echo "[INFO] Suche Branch mit requirements.txt ..."
FOUND=""
while read -r ref; do
  if git show "$ref:requirements.txt" >/dev/null 2>&1; then
    FOUND="$ref"
    break
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/remotes/origin)

if [ -z "$FOUND" ]; then
  echo "[ERR] Kein Remote-Branch enthält requirements.txt"
  echo "[HINWEIS] Prüfe, ob der Code wirklich nach GitHub gepusht wurde."
  exit 1
fi

echo "[OK] Gefunden in: $FOUND"
TARGET_BRANCH="${FOUND#origin/}"

git fetch --all --prune
if git show-ref --verify --quiet "refs/heads/$TARGET_BRANCH"; then
  git checkout "$TARGET_BRANCH"
else
  git checkout -b "$TARGET_BRANCH" "$FOUND"
fi

git pull --ff-only origin "$TARGET_BRANCH"

echo "[INFO] Prüfe Projektdateien ..."
[ -f requirements.txt ] && echo "[OK] requirements.txt" || { echo "[ERR] requirements.txt fehlt weiterhin"; exit 1; }
[ -d app ] && echo "[OK] app/" || { echo "[ERR] app/ fehlt weiterhin"; exit 1; }

echo "[NEXT] Installation:"
echo "  python3 -m venv .venv"
echo "  source .venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  uvicorn app.main:app --reload"
