# Merithra - Setup & Installation

## Entwicklungsumgebung einrichten

Dieses Dokument führt dich durch die Einrichtung der Entwicklungsumgebung für Merithra.

---

## 1. Voraussetzungen

| Anforderung | Mindestens | Empfohlen |
|-------------|------------|-----------|
| **Betriebssystem** | Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+) | Windows 11 / macosx2
| investigated, Anti w non a aEinson

sooy y5 likew y{p8 to.onesy |
| **Python** | 3.10 | 3.11+ |
| **Speicherplatz** | 500 MB | 2 GB+ (inkl. Dependencies, Assets) |
| **IDE** | Any Text Editor | VS Code oder PyCharm |
| **Git** | Installiert | Latest Version |

---

## 2. Repository Klonen

```bash
# HTTPS
git clone https://github.com/your-org/merithra.git

# SSH (falls konfiguriert)
git clone git@github.com:your-org/merithra.git

# In Verzeichnis wechseln
cd merithra
```

### 2.1 Verzeichnisstruktur nach Klon
```
merithra/
├── .git/
├── .gitignore
├── pyproject.toml          # Projekt-Konfiguration
├── requirements.txt        # Basis-Dependencies
├── requirements-dev.txt    # Dev-Dependencies
├── core/                 # Spiellogik
├── client/               # Flet UI
├── tests/                # Test-Dateien
├── docs/                 # Diese Dokumentation
├── tools/                # Hilfsmittel
└── .env.example          # Environment Variable Example (leere Werte)
```

---

## 3. Python Environment einrichten

### 3.1 Virtual Environment erstellen
```powershell
# PowerShell (Windows)
python -m venv .venv

# Activation
.\.venv\Scripts\Activate.ps1

# Bash / Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3.2 Dependencies installieren
```bash
# Basis Dependencies (Spiel-Engine, UI etc.)
pip install -e ".[dev]"

# Oder manuell (aus requirements.txt / requirements-dev.txt):
pip install flet pytest pytest-asyncio ruff mypy black hypothesis

# Optional: Für Datenbank-Features
pip install sqlalchemy asyncpg aiosqlite
```

### 3.3 IDE Konfiguration (VS Code)

**Empfohlene Extensions:**
- `ms-python.python` - Python Extension
- `ms-python.black-formatter` - Black Integration
- `ms-python.mypy-type-checker` - Type Checking
- `astral.vscode-ruff` - Linting
- `GitHub.vscode-pull-request-github` - PR Management
- `ms-azuretools.vscode-docker` (falls Docker genutzt wird)

**settings.json (VS Code):**
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.analysis.typeCheckingMode": "standard",
    "editor.formatOnSave": true,
    "editor.ruby.wordBasedSuggestions": false,
    "python.testing.pytestArgs": ["-x", "tests/"],
    "python.testing.autoTest": false,
    "files.exclude": {
        ".venv": true
    }
}
```

---

## 4. Projekt Konfiguration

### 4.1 pyproject.toml prüfen
Die zentrale Konfigurationsdatei:

```toml
[project]
name = "merithra"
version = "0.1.0"
description = "PvE-focused CCG similar to Hearthstone"
requires-python = ">=3.11"
dependencies = [
    "flet >= 0.20.0",
]

[project.optional-dependencies]
dev = [
    "pytest >= 7.0",
    "pytest-asyncio >= 0.21",
    "ruff >= 0.1.0",
    "mypy >= 1.0",
    "black >= 23.0",
    "hypothesis >= 6.0",
]

[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
select = ["I", "E", "F", "A", "B", "C", "D"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### 4.2 Environment Variables (.env)
Das `.env.example` File liegt im Root. Kopiere es und passe an:

```bash
# .env erstellen (aus .env.example kopieren)
copy .env.example .env

# Oder Linux/Mac:
cp .env.example .env

# Werte anpassen (für Phase 3+):
API_V1_STR=/api/v1
SECRET_KEY=deine-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**.env Datei ist in .gitignore enthalten** (sensible Daten nicht ins Repo!).

### 4.3 LLM-Ollama Einrichtung

Für die KI-Integration muss Ollama installiert und die gewünschten Modelle heruntergeladen werden:

```bash
# Ollama installieren (falls noch nicht geschehen):
# Windows: https://ollama.com/download herunterladen und installieren
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Empfohlenes Duo installieren (ca. 4,5 GB Gesamt):
ollama pull qwen3:4b          # Strategie-Agent (2,5-2,6 GB)
ollama pull llama3.2:3b       # Companion-LLM (2,0 GB)

# Alternative mit stärkerer Strategie (ca. 7,2 GB):
# ollama pull qwen3:8b
# ollama pull llama3.2:3b

# Installierte Modelle prüfen:
ollama list
```

**Empfohlene Hardware:**
- Mindestens 16 GB RAM für beide Standardmodelle
- IDEAL: GPU mit 6 GB VRAM für akzeptable Antwortgeschwindigkeit
- CPU-only: langsamer, aber funktionsfähig mit Qwen3 4B

Die installierten Modelle stehen dann unter `http://127.0.0.1:11434/api/chat` zur Verfügung.

---

## 5. Entwicklungsserver starten

### 5.1 Flet App lokal laufen lassen (MVP - Local Mode)
```bash
# Aus dem Projekt-Root Verzeichnis
flet run client/main.py

# Alternativ direkt mit Python
python -m client.main
```

### 5.2 Mit Browser öffnen
Flet öffnet die App im Browser. Für einen festen lokalen Web-Port:

```bash
flet run --web --host 127.0.0.1 --port 8555 client/main.py
```
Die UI ist anschließend unter `http://127.0.0.1:8555` erreichbar.

Die aktuelle MVP-Spielansicht verbindet das Flet-Board mit der State Machine:
Karten aus der Hand können gespielt, eigene Minions zum Angriff ausgewählt und
Züge beendet werden. Der KI-Gegner spielt eine bezahlbare Karte, greift nicht an
und beendet anschließend seinen Zug.

---

## 6. Test-Umgebung starten

### 6.1 Unit Tests ausführen
```bash
# Alle Tests
pytest

# Mit Coverage Report
pytest --cov=core --cov=client -x

# Nur spezifische Tests
pytest tests/core/test_engine.py -v

# GameBoard und Engine-Integration
pytest tests/test_game_board.py -v

# Verbose Mode mit Output
pytest -v --tb=long
```

### 6.2 Test-Abdeckung prüfen
```bash
# Coverage Report generieren
pytest --cov=core --cov=client

# HTML Report (öffnet sich im Browser)
pytest --cov=core --cov=client --cov-report=html

# Fail wenn Coverage unter 80%
pytest --cov=core --cov=client --cov-report=term-missing --fail-under=80
```

### 6.3 Linting & Formatierung prüfen
```bash
# Ruff Linting
ruff check .

# Black Formatierung prüfen (aber nicht ändern)
black --check .

# Auto-formatieren (ändert Dateien!)
black .

# MyPy Typ-Check
mypy --strict core/ client/
```

---

## 7. Code Quality Checks (CI-Ready)

### 7.1 Pre-commit Hooks (empfohlen)
```bash
# Pre-commit installieren
pip install pre-commit
pre-commit install

# Jetzt bei jedem Commit werden geprüft:
# - black Formatierung
# - ruff Linting
# - mypy Typ-Check (falls konfiguriert)
# - Tests (optional)

# Hooks deaktivieren (falls nötig):
pre-commit uninstall
```

### 7.2 GitHub Actions CI (ausgelagert)
Die `.github/workflows/test.yml` Datei enthält:
- `pytest` Ausführung auf jeder Änderung
- `ruff check` Linting
- `mypy` Typ-Check
- `playwright` E2E Tests (Phase 4+)

### 7.3 Lokale CI-Simulation
```bash
# Alles in einem Rüberlauf
pre-commit run --all-files

# Oder einzelne Checks:
ruff check .
black --check .
mypy --strict .
pytest --cov=core --cov=client --cov-report=term-missing
```

---

## 8. Build & Distribution (Phase 4+)

### 8.1 Desktop App Build (Flet)
```bash
# Windows Executable
flet build windows --target-dir ./dist/windows

# Mac App
flet build macos --target-dir ./dist/macos

# Linux
flet build linux --target-dir ./dist/linux
```

### 8.2 Web Build
```bash
flet build web --target-dir ./dist/web
# Oder: flet serve --port 8080
```

### 8.3 Versionierung
```bash
# Version in pyproject.toml aktualisieren
# Dann Tag erstellen
git tag -a v0.1.0 -m "Version 0.1.0 - Foundation MVP"
git push origin v0.1.0
```

---

## 9. Häufige Probleme & Lösungen

| Problem | Lösung |
|---------|--------|
| `ModuleNotFoundError: No module named 'flet'` | `pip install flet` nachvenv aktivieren |
| `ImportError: cannot import name '...' from 'core.engine'` | Ensure `.venv` is active and `pip install -e ".[dev]"` done |
| `pytest` findet keine Tests | `tests/` Verzeichnis prüfen, Dateien beginnen mit `test_` oder `_test` |
| `ruff` findet Fehler in 3rd-party Code | Konfiguration in `pyproject.toml` anpassen (`exclude = ...`) |
| Flet App startet nicht (Port already in use) | Port ändern oder bestehenden Prozess killen (`taskkill /F /IM python.exe`) |
| `mypy` type errors in Flet Code | Flet Typ-Stubs nachinstallieren: `pip install types-flet` |
| `hypothesis` Tests flaky | Einfacher lassen oder `@given` Strategien vereinfachen |

---

## 10. Optional: Docker Entwicklung (Phase 3+)

### 9.1 Dockerfile existieren (falls genutzt)
```dockerfile
# Beispiel-Dockerfile (falls für Testing genutzt)
FROM python:3.11-slim

WORKDIR /app

# Copy only needed files für schnellere Builds
COPY pyproject.toml requirements*.in ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Virtual Environment im Container
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Dependencies
RUN /venv/bin/pip install -e ".[dev]"

# Command
CMD ["flet", "run", "web", "--port", "8000"]
```

### 9.2 Docker Compose (falls Multi-Service)
```yaml
# docker-compose.yml (Phase 3+)
version: "3.9"
services:
  api:
    build: ./server/
    ports: ["8000:8000"]
    environment:
      - DEBUG=true
  
  client:
    build: ./client/
    ports: ["8550:8550"]
    depends_on: [api]
  
  db:
    image: postgres:15
    ports: ["5432:5432"]
    environment:
      - POSTGRES_DB=merithra
      - POSTGRES_USER=merithra
      - POSTGRES_PASSWORD=secret
```

---

## 11. Development Workflow Checklist

### Bei jedem Start der Entwicklung:
- [ ] `.venv` aktiviert
- [ ] `pip list` zeigt erwartete Versionen
- [ ] `ruff check .` besteht (oder `ruff .` auto-fix anwenden)
- [ ] `black .` läuft (oder Formatierung anpassen)
- [ ] Tests laufen: `pytest --tb=short` (mind. core Tests)

### Bei jedem Commit:
- [ ] Commit Message folgt Conventional Commits Format
- [ ] Geänderte Dateien geprüft (`git diff --stat`)
- [ ] Keine großen `console.log` oder `print` Debug-Ausgaben (nutze Logging)
- [ ] Test-Abdeckung im Blick behalten

### Wochentäglich:
- [ ] Code Review (eigenes oder peers Review)
- [ ] Documentation-Check (gehörte Files aktualisiert?)
- [ ] Issue Status updaten (wenn zugeordnet)
- [ ] Branch sauber halten (rebase wenn nötig)

---

## 12. Offene Setup-Fragen

- [ ] **Python Version:** 3.11 nehmen oder auf 3.12 upgraden, wenn Features benötigt?
- [ ] **Flet Version:** Stable (0.21.x) nehmen oder Nightly für neue Features?
- [ ] **Datenbank:** SQLite für MVP, wann auf PostgreSQL umsteigen?
- [ ] **CI/CD:** GitHub Actions Self-Hosted Runner einrichten oder gehostet nutzen?
- [ ] **Asset Pipeline:** Wie werden Karten-Bilder (PNG, Spine, Rive) in Projekt integriert?

---

*Dokument-Version: 1.0*  
*Status: Foundation Phase*  
*Erstellt: 2026-10-03*