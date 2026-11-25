@echo off
rem Développement : le serveur Python (API) et l'interface qui se recharge à chaque modification.
start "Serveur" cmd /k "python backend\launcher.py --no-browser"
cd frontend
if not exist node_modules call npm install
start "" http://localhost:5173
call npm run dev
