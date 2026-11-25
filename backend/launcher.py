"""Point d'entrée de l'exe : démarre le serveur local et ouvre le navigateur.

Contrat de Studio Dock (le même dans toutes les apps de la suite) :
    MonApp.exe [--port 8090] [--no-browser] [--version]
    GET /health -> {"status": "ok", "app": "<APP_ID>", "name": "<APP_NAME>", "version": "x.y.z"}
    Port imposé déjà pris par une autre application : sortie avec le code 2 (Studio Dock l'affiche).
Lancée seule (double-clic), l'app prend son port par défaut, ou un port libre, et ouvre le navigateur.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

import uvicorn

from app_info import APP_ID, APP_NAME, DEFAULT_PORT, EXE_NAME, VERSION

HOTE = "127.0.0.1"


def deja_lancee(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://{HOTE}:{port}/health", timeout=1) as reponse:
            return reponse.status == 200 and json.loads(reponse.read()).get("app") == APP_ID
    except (OSError, ValueError):
        return False


def port_libre(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOTE, port)) != 0


def un_port_libre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOTE, 0))
        return s.getsockname()[1]


def _ouvrir_quand_prete(url: str, port: int) -> None:
    for _ in range(60):
        if deja_lancee(port):
            webbrowser.open(url)
            return
        time.sleep(0.5)


def lire_options(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=EXE_NAME, description=f"{APP_NAME} : serveur local")
    parser.add_argument("--port", type=int, default=None, help=f"port d'écoute (défaut {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true", help="ne pas ouvrir le navigateur (lancement par Studio Dock)")
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {VERSION}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    options = lire_options(argv)
    port = options.port or DEFAULT_PORT
    url = f"http://{HOTE}:{port}"

    if deja_lancee(port):  # double-clic alors qu'elle tourne déjà : on la montre
        print(f"{APP_NAME} est déjà lancée sur {url}")
        if not options.no_browser:
            webbrowser.open(url)
        return

    if not port_libre(port):
        if options.port is not None:
            # Port imposé par Studio Dock : ne jamais changer en silence, il chercherait l'app au mauvais endroit
            print(f"Le port {port} est déjà utilisé par une autre application : {APP_NAME} ne peut pas démarrer.",
                  file=sys.stderr)
            sys.exit(2)
        port = un_port_libre()
        url = f"http://{HOTE}:{port}"

    print(f"{APP_NAME} {VERSION}")
    print(f"L'application est disponible sur {url}")
    print("Gardez cette fenêtre ouverte pendant l'utilisation ; fermez-la pour arrêter l'application.")
    sys.stdout.flush()

    from main import app  # importé ici : le message ci-dessus s'affiche pendant le chargement

    if not options.no_browser:
        threading.Thread(target=_ouvrir_quand_prete, args=(url, port), daemon=True).start()
    uvicorn.run(app, host=HOTE, port=port, log_level="warning")


if __name__ == "__main__":
    main()
