"""Serveur de l'app : l'API sous /api, /health pour Studio Dock, et l'interface compilée pour tout le reste."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import studiodock_ia
from app_info import APP_ID, APP_NAME, VERSION, dossier_interface

app = FastAPI(title=APP_NAME, version=VERSION)


@app.get("/health")
def sante() -> dict[str, str]:
    """Contrat de Studio Dock : répond dès que le serveur tourne, avec l'identifiant de l'app."""
    return {"status": "ok", "app": APP_ID, "name": APP_NAME, "version": VERSION}


# --- Exemple d'API : à remplacer par celle de votre app ---------------------------------------------------

class Demande(BaseModel):
    texte: str


@app.post("/api/exemple")
def exemple(demande: Demande) -> dict[str, object]:
    texte = demande.texte.strip()
    if not texte:
        raise HTTPException(status_code=422, detail="Écrivez un texte.")
    mots = texte.split()
    return {"mots": len(mots), "caracteres": len(texte), "majuscules": texte.upper()}


@app.get("/api/ia")
def ia() -> dict[str, object]:
    """Modèle d'IA réglé dans Studio Dock pour cette app (Réglages › Modèles d'IA), sans jamais renvoyer la clé."""
    choix = studiodock_ia.pour_app(APP_ID)
    if choix is None:
        return {"configure": False}
    return {"configure": True, "connexion": choix.connexion.name, "modele": choix.model, "local": choix.connexion.local}


# --- Interface compilée -------------------------------------------------------------------------------------

_INTERFACE = dossier_interface()
if (_INTERFACE / "index.html").is_file():
    if (_INTERFACE / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=_INTERFACE / "assets"), name="assets")

    @app.get("/{chemin:path}", include_in_schema=False)
    def interface(chemin: str) -> FileResponse:
        fichier = (_INTERFACE / chemin).resolve()
        if chemin and fichier.is_file() and _INTERFACE.resolve() in fichier.parents:
            return FileResponse(fichier)
        return FileResponse(_INTERFACE / "index.html")
