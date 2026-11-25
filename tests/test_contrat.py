"""Le contrat de Studio Dock : /health, --port imposé, code de sortie 2 si le port est pris."""
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from fastapi.testclient import TestClient

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "backend"))

from app_info import APP_ID, VERSION  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


def _port_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_health_repond_avec_l_identifiant_et_la_version():
    r = client.get("/health").json()
    assert r == {"status": "ok", "app": APP_ID, "name": r["name"], "version": VERSION}


def test_api_d_exemple():
    assert client.post("/api/exemple", json={"texte": "deux mots"}).json()["mots"] == 2
    assert client.post("/api/exemple", json={"texte": "  "}).status_code == 422


def test_ia_sans_studio_dock(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIODOCK_IA", str(tmp_path))
    assert client.get("/api/ia").json() == {"configure": False}


def test_lancement_par_studio_dock():
    port = _port_libre()
    process = subprocess.Popen([sys.executable, str(RACINE / "backend" / "launcher.py"), "--port", str(port), "--no-browser"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as r:
                    assert json.loads(r.read())["app"] == APP_ID
                    break
            except OSError:
                time.sleep(0.25)
        else:
            raise AssertionError("/health n'a jamais répondu")
    finally:
        process.terminate()
        process.wait(5)


def test_port_impose_deja_pris():
    with socket.socket() as occupant:
        occupant.bind(("127.0.0.1", 0))
        occupant.listen()
        port = occupant.getsockname()[1]
        code = subprocess.run([sys.executable, str(RACINE / "backend" / "launcher.py"), "--port", str(port), "--no-browser"],
                              capture_output=True, timeout=30).returncode
    assert code == 2
