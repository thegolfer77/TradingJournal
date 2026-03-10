#!/usr/bin/env bash
set -euo pipefail

ok() { echo "[OK] $1"; }
err() { echo "[ERR] $1"; }

[ -f requirements.txt ] && ok "requirements.txt gefunden" || err "requirements.txt fehlt"
[ -f Makefile ] && ok "Makefile gefunden" || err "Makefile fehlt"
[ -d app ] && ok "app/ gefunden" || err "app/ fehlt"
[ -f scripts/run.sh ] && ok "scripts/run.sh gefunden" || err "scripts/run.sh fehlt"

if command -v git >/dev/null 2>&1; then
  ok "git: $(git --version)"
else
  err "git fehlt"
fi

if command -v python3 >/dev/null 2>&1; then
  ok "python3: $(python3 --version)"
else
  err "python3 fehlt"
fi

if command -v make >/dev/null 2>&1; then
  ok "make vorhanden"
else
  err "make fehlt"
fi

if [ -f Makefile ]; then
  if grep -Eq "^run:" Makefile; then
    ok "Makefile target 'run' vorhanden"
  else
    err "Makefile target 'run' fehlt"
  fi
fi

if [ -d .venv ]; then
  ok ".venv vorhanden"
else
  err ".venv fehlt"
fi

echo "\nGit branch/commit:"
git rev-parse --abbrev-ref HEAD || true
git rev-parse --short HEAD || true
