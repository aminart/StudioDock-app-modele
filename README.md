# Modèle d'app de la suite Studio Dock

Point de départ d'une nouvelle app de la suite (SpecGen, AuditErgo, DocAnalyser…). Ce modèle contient déjà :

- **Night Navy**, le design system commun : couleurs claires et sombres, en-tête de la suite, boutons, champs,
  cases à cocher ;
- **le contrat de Studio Dock** : lancement avec `--port` et `--no-browser`, réponse sur `/health`, arrêt propre ;
  l'app se lance, s'affiche et s'arrête depuis le portail sans rien ajouter ;
- **le modèle d'IA de Studio Dock** : l'app lit celui que l'équipe a réglé dans Réglages › Modèles d'IA ;
- **la fabrication du .exe** (PyInstaller) et une icône provisoire dans le style de la suite.

Une petite page d'exemple (« Analyser un texte ») montre les composants en action : remplacez-la par votre app.

Guide complet des règles de la suite : document « Faire une app de la suite Studio Dock ».

## En 5 étapes

### 1. Copier le modèle

Sur GitHub : bouton **Use this template › Create a new repository**, puis récupérez votre dépôt sur votre poste
(GitHub Desktop, ou `git clone`).

Prérequis : Python 3.11 ou plus, Node.js 20 ou plus.

### 2. Donner son nom à l'app

```
python scripts/renommer.py "Nom de l'app" --port 8110
```

Le script remplit `backend/app_info.py` (identifiant, nom, programme, port) et le titre de la page. **Le port doit
être unique dans la suite** : 8010 (SpecGen), 8020 (DocAnalyser), 8501 (AuditErgo) et 8030 à 8080 (apps ajoutées par
Studio Dock) sont pris. Demandez à la personne qui gère le catalogue de l'équipe.

### 3. Développer

```
pip install -r requirements-dev.txt
cd frontend && npm install && cd ..
start_dev.bat
```

`start_dev.bat` lance le serveur Python et l'interface sur http://localhost:5173 : chaque modification de
l'interface s'affiche tout de suite. Sur Mac : `python backend/launcher.py --no-browser` dans un terminal,
`cd frontend && npm run dev` dans un autre.

- **Interface** : `frontend/src/App.tsx`. Gardez l'en-tête (`nn-appbar`) et le titre de page (`nn-page-head`) ;
  utilisez les classes du design system (`bg-surface`, `text-ink`, `text-accent`, `nn-btn`, `nn-card`…) plutôt que
  des couleurs écrites en dur.
- **API** : `backend/main.py`, sous `/api/…`. Ne touchez pas à `/health`.
- **IA** : `studiodock_ia.pour_app(APP_ID)` donne la connexion et le modèle réglés dans Studio Dock (exemple :
  route `/api/ia`). Ne recopiez jamais la clé dans l'interface ni dans un journal.
- **Tests** : `python -m pytest`. Ceux de `tests/test_contrat.py` vérifient le contrat de Studio Dock : ils doivent
  toujours passer.

### 4. Lui donner son icône

Remplacez les trois fichiers du dossier `icone/` : `app.svg`, `app-petit.svg` (version simplifiée pour les petites
tailles) et `app.ico`. Pour une icône dans le style de la suite, demandez à Claude avec le skill
« icône app suite ». Le script `scripts/fabriquer_icones.py` produit le `.ico` à partir des deux SVG.

Seule l'icône a la couleur propre de l'app : tout le reste suit Night Navy.

### 5. Fabriquer l'exe et l'ajouter au portail

```
build_exe.bat
```

L'exe est dans `dist\`. Pour le diffuser :

1. Renommez-le avec sa version, par exemple `NomDeLApp-0.1.0.exe`.
2. Dans Studio Dock, onglet **Préparer pour l'équipe › Applications**, ajoutez l'app : type « S'ouvre dans le
   navigateur », icône `icone/app.svg`, et sa fiche (à quoi elle sert, prise en main).
3. Déposez l'exe dans le sous-dossier de l'app, dans le dossier de l'équipe.

Pour une nouvelle version : notez les changements dans `CHANGELOG.md` (« Non publié »), puis
`python scripts/bump_version.py 0.2.0`, fabriquez l'exe et déposez-le avec son nouveau numéro.

## Ce qu'il y a dans le modèle

| Fichier | Rôle |
|---|---|
| `backend/app_info.py` | Identité de l'app : le seul fichier à adapter (ou `scripts/renommer.py`). |
| `backend/launcher.py` | Point d'entrée de l'exe : contrat de Studio Dock. À ne pas modifier. |
| `backend/main.py` | Serveur : `/health`, votre API, l'interface compilée. |
| `backend/studiodock_ia.py` | Lecture des modèles d'IA de Studio Dock. Copie : ne pas modifier. |
| `frontend/` | Interface React + Tailwind avec Night Navy (`night-navy` dans `package.json`). |
| `icone/` | Icône de l'app : SVG, petite version, `.ico`. |
| `app.spec`, `build_exe.bat`, `build_exe_mac.sh` | Fabrication de l'exe. |
| `scripts/` | Renommer l'app, changer de version, fabriquer les icônes. |
| `tests/` | Tests du contrat et de l'API d'exemple. |

## Le contrat de Studio Dock, en bref

```
NomDeLApp.exe [--port 8110] [--no-browser] [--version]
GET /health -> {"status": "ok", "app": "<APP_ID>", "name": "<APP_NAME>", "version": "x.y.z"}
```

- `--port` imposé et déjà pris par une autre application : l'app s'arrête avec le code 2 (Studio Dock l'affiche).
- `--no-browser` : Studio Dock ouvre lui-même le navigateur.
- Lancée seule (double-clic), l'app prend son port par défaut, ou un port libre, et ouvre le navigateur.
- L'`app` renvoyée par `/health` est l'identifiant de l'app dans le catalogue de Studio Dock.
