"""Donne son identité à l'app, en une commande, juste après avoir copié le modèle.

    python scripts/renommer.py "Snappy Notes"                 # identifiant et programme déduits du nom
    python scripts/renommer.py "Snappy Notes" --port 8110     # port choisi
    python scripts/renommer.py "Snappy Notes" --id notes --exe SnappyNotes

Met à jour backend/app_info.py (source de vérité), le titre de la page, le nom du paquet de l'interface et le
port du serveur de développement. Ne touche pas au contenu des pages.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# Ports déjà pris par les apps de la suite : SpecGen, DocAnalyser, AuditErgo, et ceux que Studio Dock attribue
# aux apps ajoutées par son formulaire (8030, 8040…). À compléter si l'équipe en réserve d'autres.
PORTS_DE_LA_SUITE = {8010, 8020, 8501} | set(range(8030, 8090, 10))


def _ascii(nom: str) -> str:
    return unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()


def _remplacer(textes: dict[Path, str], fichier: Path, motif: str, par: str, tous: bool = False) -> None:
    """Remplacement préparé en mémoire : rien n'est écrit tant que tous les motifs n'ont pas été trouvés."""
    texte = textes.setdefault(fichier, fichier.read_text(encoding="utf-8"))
    nouveau, n = re.subn(motif, par, texte, count=0 if tous else 1, flags=re.M)
    if not n:
        raise SystemExit(f"{fichier.relative_to(RACINE)} : « {motif} » introuvable, fichier modifié à la main ? "
                         "Rien n'a été changé.")
    textes[fichier] = nouveau


def main() -> None:
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("nom", help="nom affiché de l'app")
    options.add_argument("--id", help="identifiant (minuscules, chiffres, tirets) ; défaut : déduit du nom")
    options.add_argument("--exe", help="nom du programme sans .exe ; défaut : le nom sans espaces ni accents")
    options.add_argument("--port", type=int, help="port réservé à l'app ; défaut : celui du modèle (8090)")
    args = options.parse_args()

    nom = args.nom.strip()
    ident = args.id or re.sub(r"[^a-z0-9]+", "-", _ascii(nom).lower()).strip("-")
    exe = args.exe or "".join(m[:1].upper() + m[1:] for m in re.split(r"[^A-Za-z0-9]+", _ascii(nom)) if m)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", ident) or not exe:
        raise SystemExit("Nom, identifiant ou programme invalide : précisez --id et --exe.")
    if args.port is not None and not 1024 <= args.port <= 65535:
        raise SystemExit("Le port doit être entre 1024 et 65535.")
    if args.port in PORTS_DE_LA_SUITE:
        raise SystemExit(f"Le port {args.port} est déjà celui d'une app de la suite : choisissez-en un autre.")

    textes: dict[Path, str] = {}
    info = RACINE / "backend" / "app_info.py"
    _remplacer(textes, info, r'^APP_ID = "[^"]*"', f'APP_ID = "{ident}"')
    _remplacer(textes, info, r'^APP_NAME = .*?(?=  #|$)', f'APP_NAME = {json.dumps(nom, ensure_ascii=False)}')
    _remplacer(textes, info, r'^EXE_NAME = "[^"]*"', f'EXE_NAME = "{exe}"')
    if args.port:
        _remplacer(textes, info, r"^DEFAULT_PORT = \d+", f"DEFAULT_PORT = {args.port}")
        _remplacer(textes, RACINE / "frontend" / "vite.config.ts", r"127\.0\.0\.1:\d+", f"127.0.0.1:{args.port}", tous=True)
    _remplacer(textes, RACINE / "frontend" / "index.html", r"<title>.*</title>", f"<title>{html.escape(nom)}</title>")
    paquet = RACINE / "frontend" / "package.json"
    donnees = json.loads(paquet.read_text(encoding="utf-8"))
    donnees["name"] = f"{ident}-interface"
    textes[paquet] = json.dumps(donnees, indent=2, ensure_ascii=False) + "\n"
    for fichier, texte in textes.items():
        fichier.write_text(texte, encoding="utf-8")

    print(f"{nom} : identifiant « {ident} », programme {exe}.exe"
          + (f", port {args.port}" if args.port else " (port du modèle : 8090, à changer s'il est déjà pris)") + ".")
    print("Ensuite : remplacez icone/app.svg, app-petit.svg et app.ico par l'icône de l'app (voir le README).")


if __name__ == "__main__":
    main()
