# Merithra - Beitragsleitfaden

## Wir freuen uns über Beiträge!

Wir schätzen jede Beiträge zu Merithra. Egal ob Bug-Reports, Feature-Ideen oder Code-Änderungen - hilf uns, das Projekt zu verbessern.

---

## 1. Code of Conduct

Bitte beachte folgende Grundsätze:

- **Respektvoll:** Unterschiedliche Sichtweisen und Erfahrungen willkommen
- **Konstruktiv:** Feedback zielt auf Verbesserung, nicht auf Kritik
- **Inklusiv:** Jeder soll sich willkommen fühlen, unabhängig von Hintergrund
- **Professionell:** Konstruktive Kommunikation, keine persönlichen Angriffe

Verstöße können zu einem temporären oder permanenten Ausschluss aus dem Projekt führen.

---

## 2. Wie man Beiträge leistet

### 2.1 Issue erstellen
Bevor du Code schreibst, erstelle ein Issue für:
- Bug-Reports mit Schritten zur Reproduktion
- Feature-Anfragen mit Use-Case Beschreibung
- Verbesserungsvorschläge

### 2.2 Feature Branch erstellen
```bash
# Von dev Zweig abzweigen
git checkout dev
git pull origin dev

# Neuen Feature-Branch erstellen
git checkout -b feat/kurzer-beschreibung-des-features
# Oder: git checkout -b fix/bug-beschreibung
```

### 2.3 Entwicklung
- Halte dich an die Code-Conventions in diesem Dokument
- Schreib Unit Tests für neue Funktionen
- Aktualisiere die Dokumentation bei Bedarf
- Lade regelmäßig Changes hoch (git push)

### 2.4 Pull Request erstellen
- Titel soll klar beschreiben, was geändert wurde
- Beschreibung soll enthalten:
  - Was wurde geändert und warum
  - Which Issue es schließt (Closes #123)
  - Getestet wurde an welchen Stellen
  - Screenshots bei UI-Änderungen
- Füge `Reviewers` hinzu (mind. 1 CODE_REVIEWER)

### 2.5 Review Prozess
1. **Automatische Checks:** CI muss bestehen (Tests, Lint, Type Check)
2. **Code Review:** mind. 1 Mitglied nimmt Review vor
3. **Address Feedback:** Changes implementieren und pushen
4. **Merge:** Maintainer merge nach erfolgreichem Review

---

## 3. Code-Conventions

### 3.1 Python Style
- **PEP 8** als Basis
- **Black** für Code Formatierung (automatisch via Pre-commit)
- **isort** für Imports
- Typ-Hinweise (`type hints`) für alle öffentlichen Funktionen

```python
# Richtig
def play_card(self, card_id: str, target: str | None = None) -> GameResult:
    """Spiel eine Karte mit optionalem Ziel."""
    ...

# Falsch
def play_card(card_id, target):
    ...
```

### 3.2 Import Order
```python
# Standard Library
import os
import json
import logging

# Third Party
import flet
import pytest
import hypothesis

# Project Local
from core.engine import StateMachine
from core.cards import CardRegistry
from client.flet_ui import GameBoard
```

### 3.3 Naming Conventions
- **Functions:** `snake_case` (z. B. `play_card()`, `calculate_damage()`)
- **Classes:** `PascalCase` (z. B. `GameEngine`, `CardRegistry`)
- **Constants:** `UPPER_SNAKE_CASE` (z. B. `MAX_MANA`, `STARTING_HP`)
- **Variables:** `lower_snake_case` (z. B. `current_mana`, `player_hero`)
- **Keywords/Enums:** `UPPER_SNAKE_CASE` (z. B. `CARD_TYPE_MINION`, `PHASE_MAIN`)

### 3.4 Dokumentation
- Docstrings für alle öffentlichen Funktionen (Google Style oder NumPy Style)
- Module-level Docstrings erklären Zweck der Datei
- Kommentare nur bei Nicht-Offensichtlichem verwenden

### 3.5 Error Handling
- Exceptions statt Return-Codes für Fehlerbedingungen
- Custom Exceptions sind präzise benannt

```python
# Richtig
class InsufficientManaError(Exception):
    pass

# Falsch
def play_card(...):
    if not enough_mana:
        return False  # Caller muss jeden Return prüfen
```

---

## 4. Git Workflow

### 4.1 Branch Strategy
```
main:   Production-ready, getaggte Releases
dev:    Integrierende Zweig, nächste Release-Vorlage
feature/*: Kurzlebige Feature-Zweige (max. 1-2 Wochen)
hotfix/*: Critical Bugs in main, dann nach dev merge
```

### 4.2 Commit Conventions (Angeschlossen an Conventional Commits)
```
<typ>: <betreff>

# Beispiele:
feat:   Neue Karten-Keyword-Implementierung
fix:    Bug: Karte spielt sich nicht
docs:   Architecture-README aktualisiert
refactor: Engine State Machine Optimierung
test:   Neue Unit Tests für Boss AI
chore:  Pre-commit Hooks hinzugefügt
```

### 4.3 Pull Request Template
Jeder PR muss das Template ausfüllen:
- Description of Changes
- Related Issue(s)
- Testing performed
- Screenshots (if UI changed)
- Checklist:
  - [ ] Code Conventions befolgt
  - [ ] Unit Tests hinzugefügt/geändert
  - [ ] Documentation aktualisiert
  - [ ] Keine Secrets im Code
  - [ ] CI/CD Checks bestehen

### 4.4 Git-Verbotene Aktionen
- Kein `git reset --hard` ohne Backup
- Kein `git force push` auf `dev` oder `main` ohne Review
- Kein direktes Commit auf `main`
- Kein `git clean` ohne ausdrückliche Erlaubnis

---

## 5. Entwicklungsumgebung Setup

### 5.1 Voraussetzungen
- **Python 3.11+** (empfohlen: 3.12)
- **Git** für Versionskontrolle
- **IDE/Editor:** VS Code oder PyCharm (empfohlen mit Python Extension)
- **Optional:** Node.js (falls Flet Web-Specific Features genutzt werden)

### 5.2 Repository Klonen
```bash
git clone https://github.com/your-org/merithra.git
cd merithra
```

### 5.3 Virtual Environment einrichten
```bash
# Virtual Environment erstellen
python -m venv .venv

# Aktivieren (PowerShell)
.\.venv\Scripts\Activate.ps1

# Aktivieren (Bash/Linux/Mac)
source .venv/bin/activate

# Dependencies installieren
pip install -e ".[dev]"
```

### 5.4 Entwicklung Dependencies
Die `pyproject.toml` oder `requirements-dev.txt` enthält:
- `pytest` + `pytest-asyncio` für Tests
- `ruff` für Linting/Formatierung
- `mypy` für Typ-Checking
- `black` für Code Formatierung
- `hypothesis` (optional, Property-Based Testing)
- `flet` (neueste Stable Version)
- Abhängigkeiten aus `requirements.txt`

### 5.5 Projektstruktur nach Setup
Nach `pip install -e ".[dev]"` sollte folgende Struktur funktionieren:
```
merithra/
├── core/           # Spiellogik
├── client/         # Flet UI
├── tests/          # Test-Dateien
├── docs/           # Diese Dokumentation
├── tools/          # Hilfsmittel (Card Editor etc.)
└── pyproject.toml  # Projekt-Konfiguration
```

### 5.6 Lokalen Server starten (falls benötigt)
```bash
# Für lokale Tests (Phase 3+)
python -m uvicorn server.main:app --reload --port 8000

# Oder Flet Web Server
flet run web --port 8080

# UI nur lokal (MVP)
python -m client.main
```

---

## 6. Test-Richtlinien

### 6.1 Unit Tests schreiben
- Jede neue Funktion erhält Unit Tests
- Tests liegen nebeneinander im Modul: `tests/core/test_engine.py`
- Test-Namen beschreiben das Szenario: `test_play_card_when_enough_mana`

### 6.2 Integration Tests
- Komplette Game Flows durchspielen
- `pytest` mit `--cov` für Coverage Reports
- CI integriert Tests bei jedem Push

### 6.3 Test Data
- Test-Karten und -Encounters in `tests/fixtures/` ablegen
- Keine harten Referenzen auf echte Card-IDs in Test-Logik
- Fixtures werden bei Tests geladen via `tests/fixtures/loader.py`

### 6.4 Code Coverage Ziele
- **Phase 1 (MVP):** > 80% für `core/engine` und `core/cards`
- **Phase 2 (PvE):** > 70% Gesamtprojekt
- **Phase 3 (Multiplayer):** > 60% (netzwerkbedingte Komplexität)

---

## 7. Documentation Guidelines

### 7.1 Was dokumentiert wird
- **Architektur-Entscheidungen** (ARCHITECTURE.md)
- **API-Referenz** (API.md)
- **Roadmap & Meilensteine** (ROADMAP.md)
- **Konzept-Overview** (Konzept.md - bereits existiert)
- **Security-Richtlinien** (SECURITY.md)
- **Test-Strategie** (TESTING.md)

### 7.2 Dokumentations-Standards
- Markdown Format (`.md` Files)
- Consistent Headers (H1, H2, H3 Struktur)
- Code Blocks mit Syntax-Highlighting
- Tables für Vergleiche und Übersichten
- Keine generierten Texte ohne Prüfung

### 7.3 Dokumentation aktualisieren
Bei jeder signifikanten Änderung:
1. Prüfe, welche Dokumente affected sind
2. Aktualisiere betroffene Files
3. Füge Changes in CHANGELOG.md (falls existent) ein
4. Markiere in ROADMAP.md wenn Meilenstein erreicht

### 7.4 Verbotene Documentation-Praktiken
- Keine unverifizierten Behauptungen in Dokumentation
- Keine "TODO: später docs aktualisieren" als Abschluss hinterlassen
- Keine Dokumentation, die dem Code widerspricht

---

## 8. Issue Triage & Management

### 8.1 Label Schema (GitHub Issues)
| Label | Bedeutung | Nutzung |
|-------|-----------|---------|
| `bug` | Etwas funktioniert nicht | Bug-Reports |
| `feature` | Neue Funktionalität gewünscht | Feature-Anfragen |
| `enhancement` | Verbesserung bestehenden Features | UX/Performance |
| `good first issue` | Perfekt für Neueinsteiger | Onboarding |
| `help wanted` | Unterstützung benötigt | Wichtige Tickets |
| `question` | Klärungsbedarf | Verständnisfragen |
| `documentation` | Doc-only Änderung | Docs |
| `performance` | Performance-relevant | Profiling needed |
| `security` | Sicherheitsbedenken | Sofort attention |

### 8.2 Priorisierung
- **Critical:** Game-crashing Bugs, Security Issues
- **High:** Kern-Features blockiert, Balance-Probleme
- **Medium:** QoL-Verbesserungen, Nicht-kritische Bugs
- **Low:** Cosmetic Issues, Wünschenswerte Extras

### 8.3 Meilenstein-Zuordnung
Issues sollten einem Meilenstein in ROADMAP.md zugeordnet werden:
- `M1`-`M8`: Phase 1 Foundation
- `M9`-`M16`: Phase 2 PvE Content
- `M17`-`M24`: Phase 3 Multiplayer
- `M25`-`M32`: Phase 4 Polish
- `Post-Launch`: Phase 5 Erweiterungen

---

## 9. Häufige Aufgaben & Ansprechpartner

### 9.1 Bei Architektur-Fragen
- **CODE_ARCHITECT** konsultieren vor größeren Änderungen
- Änderungen an Datenmodellen oder Schnittflächen

### 9.2 Bei Implementierung
- **CODE_IMPLEMENTOR** für Code-Entwicklung
- Unit Tests und Integration Tests sicherstellen

### 9.3 Bei Tests
- **TEST_ENGINEER** für Test-Strategie
- Test-Abdeckung überwachen und ausbauen

### 9.4 Bei UI/Flet-Fragen
- **FRONTEND_SPECIALIST** für Interface-Design
- Accessibility und Responsive Design prüfen

### 9.5 Bei Security
- **SECURITY_AUDITOR** für Security-Review
- Bei Changes an Auth, Secrets, MCP

### 9.6 Bei Datenbank
- **DATABASE_SPECIALIST** für Schema-Änderungen
- Migrationen und Rollback-Pläne

### 9.7 Bei Performance
- **PERFORMANCE_OPTIMIZER** für Profiling
- Optimierungen müssen messbar sein

### 9.8 Bei DevOps/Deployment
- **DEVOPS_ENGINEER** für CI/CD Pipeline
- Docker, Container, Release-Process

### 9.9 Bei API-Integration
- **API_INTEGRATION_SPECIALIST** für Endpoints
- Verträge und Authentifizierung

### 9.10 Bei Bugs
- **BUG_HUNTER** für Debugging und Root-Cause-Analyse
- Regression Tests sicherstellen

---

## 10. Anerkennung

Alle Beiträge werden in der `CONTRIBUTORS.md` Datei vermerkt (automatisch via `git log` oder manuell).

**Contributor Levels:**
- **🥉 Bronze:** Erstmaliger Beitrag (Issue oder kleiner Fix)
- **🥈 Silber:** 5+ Commits oder Feature completion
- **🥇 Gold:** Major Feature completion oder Architecture contribution
- **💎 Diamond:** Significant Project Maintenance oder Langzeit-Beteiligung

---

## 11. Frequently Asked Questions (FAQ)

### Q: Ich habe keine Erfahrung mit Flet. Soll ich trotzdem mitmachen?
**A:** Ja! Wir haben eine Lernkurve, und FRONTEND_SPECIALIST steht zur Verfügung. Fang mit kleinen UI-Anpassungen an.

### Q: Wie oft sollte ich commits machen?
**A:** Häufig, kleine Commits sind besser als große "alles-auf-einmal"-Commits. Jeder Commit sollte eine logische Einheit sein.

### Q: Was passiert, wenn meine Pull Request abgelehnt wird?
**A:** Kein Problem! Das Review ist konstruktiv. Bitte die Feedback implementieren und erneut einreichen.

### Q: Dürfe ich an der Konzept.md mitarbeiten?
**A:** Ja, aber nur in Absprache mit SUPERVISOR (dem zentralen Coordinator). Große architekturelle Änderungen müssen von CODE_ARCHITECT genehmigt werden.

### Q: Gibt es eine Code of Conduct Verletzung Policy?
**A:** Verstöße werden von SUPERVISOR geprüft und je nach Schweregrad gemahnt oder excluded.

---

## 12. Nächste Schritte für Neueinsteiger

1. **Repository forken** und klonen
2. **Virtual Environment** einrichten (siehe Abschnitt 5)
3. **Ersten Issue** suchen (Label `good first issue`)
4. **Feature Branch** erstellen
5. **Kleinen Fix oder Feature** implementieren
6. **Tests** schreiben
7. **Pull Request** erstellen und Review erwarten
8. **Feedback** implementieren und merge lassen

---

*Dokument-Version: 1.0*  
*Status: Foundation Phase*  
*Erstellt: 2026-10-03*  
*Zuletzt aktualisiert: 2026-10-03*