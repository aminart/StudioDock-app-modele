"""Identité de l'app : le seul fichier à adapter (ou : python scripts/renommer.py "Nom de l'app").

Utilisée par /health (contrat de Studio Dock), le lanceur, la fabrication de l'exe et l'en-tête de l'interface.
La version vient du fichier VERSION à la racine (source unique, embarquée dans l'exe).
"""
from __future__ import annotations

import sys
from pathlib import Path

APP_ID = "mon-app"  # identifiant : minuscules, chiffres et tirets ; c'est aussi l'id dans le catalogue de Studio Dock
APP_NAME = "Mon app"  # nom affiché (en-tête, Studio Dock)
EXE_NAME = "MonApp"  # nom du programme : MonApp.exe, sans espace ni version
DEFAULT_PORT = 8090  # port réservé à l'app ; deux apps de la suite n'ont jamais le même


def _racine() -> Path:
    """Dossier des fichiers embarqués (exe PyInstaller) ou racine du dépôt (développement)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def _lire_version() -> str:
    try:
        return (_racine() / "VERSION").read_text(encoding="utf-8").strip() or "0.0.0"
    except OSError:
        return "0.0.0"


VERSION = _lire_version()


def dossier_interface() -> Path:
    """Interface compilée (frontend/dist), embarquée dans l'exe sous « interface »."""
    if getattr(sys, "frozen", False):
        return _racine() / "interface"
    return _racine() / "frontend" / "dist"
