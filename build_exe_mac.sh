#!/bin/sh
# Fabrique dist/<NomDuProgramme> sur Mac ou Linux. Prérequis : Python 3.11+ et Node.js 20+.
set -e
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt pyinstaller
cp icone/app.svg frontend/public/icone.svg
(cd frontend && npm ci && npm run build)
pyinstaller --noconfirm app.spec
echo "Terminé : l'exe est dans le dossier dist."
