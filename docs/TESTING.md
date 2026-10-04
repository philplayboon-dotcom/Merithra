# Merithra - Teststrategie & Qualitätssicherung

## Versionsverwaltung
- **Version:** 1.0
- **Status:** Foundation Phase
- **Zuletzt aktualisiert:** 2026-10-03

---

## 1. Test-Pyramide

```text
        +----------------------+
        |   E2E / Integration  |
        |   (Selenium, Playwright)|
        +----------+-----------+
                   |
        +----------v-----------+
        |   Integration Tests  |
        |   (pytest, httpx)    |
        +----------+-----------+
                   |
        +----------v-----------+
        |   Unit Tests         |
        |   (pytest, unittest) |
        +----------+-----------+
                   |
        +----------v-----------+
        |   Static Analysis    |
        |   (mypy, ruff)       |
        +----------------------+
```

### Test-Verteilung (Geplant)

| Ebene | Ziel | Aufwand | Verantwortung |
|-------|------|---------|---------------|
| **Unit Tests** | 70-80% aller Tests | Gering | CODE_IMPLEMENTOR, CODE_ARCHITECT |
| **Integration Tests** | 15-20% aller Tests | Mittel | TEST_ENGINEER |
| **LLM Tests** | 5% aller Tests | Mittel | TEST_ENGINEER |
| **E2E Tests** | 5-10% aller Tests | Hoch | TEST_ENGINEER + BUG_HUNTER |
| **Manual Testing** | Ad-hoc & Release | Variabel | SUPERVISOR + ALLE |

---

## 2. Unit Tests (Core Engine)

### 2.1 Abgedeckte Module
- `core/engine` State Machine Übergänge
- `core/cards` Effect Anwendung, Validierung
- `core/pme` Encounter-Basics (Schaden, Leben)
- `core/guild` Grund-Operationen

### 2.2 Test-Rahmenwerk
- **pytest** als Standard
- **pytest-asyncio** für async-Tests
- **hypothesis** für Property-Based Testing (optional)
- **Coverage** Ziel: > 80% für Phase 1, > 70% für Gesamtprojekt

### 2.3 Test-Beispiel-Struktur

```python
# tests/engine/test_state_machine.py
import pytest
from core.engine import StateMachine, GamePhase

def test_mulligan_to_turn_start():
    """MULLIGAN Phase → TURN_START Übergang ist valid."""
    # Arrange
    sm = StateMachine()
    sm.set_phase(GamePhase.MULLIGAN)
    player = sm.player
    
    # Act
    result = sm.next_phase()
    
    # Assert
    assert result.phase == GamePhase.TURN_START
    assert player.mulligan_complete == True

def test_insufficient_mana():
    """Nicht genug Mana zum Karten-Spielen."""
    # Arrange
    sm = StateMachine()
    card_cost = 5
    
    # Act & Assert
    with pytest.raises(InvalidActionError, match="Not enough mana"):
        sm.play_card(card_id="spell_001", target=None)
```

### 2.4 Quality Gates (Unit)
- [ ] Alle neuen Funktionen haben Unit Tests
- [ ] Kein Commit ohne Unit Test Abdeckung Erhöhung
- [ ] `pytest` läuft mit 100% success rate
- [ ] Coverage Report generiert und geprüft

---

## 3. Integration Tests

### 3.1 Abgedeckte Szenarien
- Vollständige Partie Human vs AI
- Deck Builder Validierung (30 Karten, Legalitäts-Check)
- Karten-Zersetzung → Crafting Economy
- Belohnung-verteilung nach Mission
- **LLM Strategy Agent: Zug-Vorschlag Validierung**
- **LLM Companion: Konversationsfähigkeit Test**

### 3.2 Test-Struktur

```python
# tests/llm/test_strategy_agent.py
import json
import pytest
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
        "turn": 8,
        "myMana": 5,
        "myHealth": 21,
        "enemyHealth": 14,
        "myBoard": [{"id": "wolf", "attack": 3, "health": 2, "canAttack": True}],
        "enemyBoard": [{"id": "golem", "attack": 4, "health": 5, "taunt": True}],
        "hand": [{"id": "fireball", "cost": 4}, {"id": "bear", "cost": 5}],
        "legalActions": [
            {"type": "attack", "attacker": "wolf", "target": "golem"},
            {"type": "play_card", "card": "fireball", "target": "golem"},
            {"type": "play_card", "card": "bear"},
            {"type": "end_turn"}
        ]
    }
    
    # Act
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3:4b",
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": "Du bist ein Kartenspiel-Strategie-Agent. Wähle ausschließlich eine Aktion aus legalActions. Antworte ausschließlich als JSON."},
                {"role": "user", "content": str(state)}
            ],
            "options": {"temperature": 0.3, "num_predict": 160}
        }
    )
    decision = response.json()["message"]["content"]
    move = json.loads(decision)
    
    # Assert
    assert move["action"] in ["attack", "play_card", "end_turn"]
    assert "card" not in move or move.get("card") in ["fireball", "bear"]
    assert "target" in move or move.get("action") == "end_turn"

def test_companion_no_hidden_info():
    """Companion-LLM darf keine verdeckten Informationen preisgeben."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3.2:3b",
            "stream": False,
            "messages": [
                {"role": "system", "content": "Du bist Rook, ein Kartenmeister. Erkläre Züge, ohne verdeckte Karten zu sehen."},
                {"role": "user", "content": "Was hältst du von meinem Zug?"}
            ]
        }
    )
    answer = response.json()["message"]["content"]
    
    # Assert - should not contain card names, health values, etc. that are hidden
    # This is a basic check - real implementation would be more thorough
    assert "hidden" not in answer.lower() or "Ich sehe" not in answer

```python
# tests/integration/test_full_game.py
def test_human_vs_ai_game():
    """Komplette Partie gegen KI durchspielen."""
    from game import new_game
    
    # Arrange
    game = new_game(mode="AI", difficulty=" easy")
    
    # Act - kompletter Spielablauf
    while not game.is_over():
        action = game.get_player_action()
        game.execute_action(action)
    
    # Assert
    winner = game.get_winner()
    assert winner in [PLAYER_HUMAN, PLAYER_AI]
    assert game.rewards.gold > 0
    assert len(game.rewarded_cards) >= 0
```

### 3.3 Qualitätssicherung
- [ ] Mindestens 1 komplettes Spiel pro Tag im CI
- [ ] Desync-Tests für deterministische Replays
- [ ] Load-Tests für UI-Performance (Flet)

---

## 4. E2E Tests (End-to-End)

### 4.1 Tool-Optionen
- **Playwright** (empfohlen: Auto-Wait, Multi-Browser)
- **Selenium** (Legacy, aber weit verbreitet)
- **Custom Flet Tests** (via `page.run_javascript`)

### 4.2 E2E Test-Szenarien

| Szenario | Beschreibung | Priorität |
|----------|--------------|-----------|
| **New Game Flow** | MainMenu → DeckBuilder → Game → Results | High |
| **Card Play** | Drag & Drop von Hand auf Board | High |
| **Keyword Resolution** | Taunt, Charge, Battlecry etc. | Medium |
| **Save & Load** | Spielstand speichern & laden | Medium |
| **Menu Navigation** | Alle Menüs navigierbar | Low |
| **Accessibility** | Screen Reader Tags vorhanden | Low |

### 4.3 CI-Integration
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: {python-version: "3.11"}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=core --cov=client -x
      - run: playwright test --project=chromium
      - run: coverage report --fail-under=80
```

---

## 5. Property-Based Testing (Optional, Phase 2+)

### 5.1 Beispiele mit Hypothesis
```python
from hypothesis import given, strategies as st
from core.engine import play_card_validator

# Jede Karte darf nur gespielt werden wenn genug Mana vorhanden ist
@given(st.integers(min=0, max=10), st.text(min_length=1))
def test_mana_validation(mana, card_id):
    engine = Engine(start_mana=mana)
    # Property: Karte mit Kosten > start_mana kann nicht gespielt werden
    with pytest.raises(InsufficientManaError):
        engine.play_card(card_id, target=target)
```

### 5.2 Nutzen
- Edge Cases automatisch entdecken
- Boundary Conditions testen
- Reduced Test Maintenance

---

## 6. Bug Hunting & Regression

### 6.1 BUG_HUNTER Workflow
1. **Reproduktion:** Bug in isolierter Umgebung reproduzieren
2. **Root Cause:** Fehlerquelle identifizieren (Engine, UI, Data)
3. **Fix:** Implementierung der Lösung
4. **Regression Test:** Neuen Test hinzufügen, damit Bug nicht wiederkehrt
5. **Verification:** Test in verschiedenen Szenarien laufen lassen

### 6.2 Regression Prevention
- Jeder Bugfix benötigt einen Unit- oder Integration-Test
- Test name beschreibt den Fix: `test_play_card_insufficient_mana_post_fix`
- Test in `tests/regressions/` Verzeichnis ablegen

---

## 7. Performance Testing

### 7.1 Metriken (Flet UI)
- **Frame Rate:** 60 FPS Desktop, 30 FPS Mobile Target
- **Memory:** Keine Leaks nach 2h kontinuierlichem Spiel
- **Startzeit:** Game Board < 2 Sekunden nach Deck Selection
- **Animationsdauer:** Karten-Spielen < 500ms

### 7.2 Tools
- `page.show_at` für Window Positionierung
- `time` module für Execution Time Messung
- Custom Profiler in Flet `on_frame` Events
- `memory_profiler` für Python-Side Leaks

### 7.3 Performance Test-Beispiel
```python
def test_gameboard_performance():
    """Flet GameBoard Performance Baseline."""
    from client import GameBoard
    
    board = GameBoard()
    
    # 50 Karten auf Board platzieren
    board.populate_board(50)
    
    # Performance messen
    start = time.time()
    board.render()
    elapsed = time.time() - start
    
    # Assert: Rendern soll < 2s auf Referenz-Hardware
    assert elapsed < 2.0, f"Render too slow: {elapsed}s"
```

---

## 8. Code Quality & Static Analysis

### 8.1 Linting
- **ruff** (schneller als flake8 + black)
- Konfiguration in `pyproject.toml`

```toml
[tool.ruff]
line-length = 88
select = ["I", "E", "F", "A", "B", "C", "D"]
exclude = [".git", "__pycache__", "*.pyc"]
```

### 8.2 Typprüfung
- **mypy** mit `strict = True` für Core-Module
- Typ-Stubs für Flet-UI-Komponenten
- Optional: `pyright` als Alternative

### 8.3 Quality Gates (CI)
```yaml
# Beispiel CI Check
- name: Lint & Type Check
  run: |
    ruff check .
    mypy --strict core/ client/
  
- name: Test Suite
  run: |
    pytest --cov=core --cov=client -x
    coverage report -m
    # Fail if coverage < 80%
```

---

## 9. Test-Daten & Fixtures

### 9.1 Test-Daten Verzeichnis
```
tests/
├── fixtures/
│   ├── cards/
│   │   ├── card_minion_001.json
│   │   └── card_spell_001.json
│   ├── encounters/
│   │   └── boss_test_001.yaml
│   └── decks/
│       ├── deck_basic.json
│       └── deck_ai.json
└── integration/
    └── saves/
        └── game_state_001.json
```

### 9.2 Fixture-Beispiel
```yaml
# tests/fixtures/cards/card_test_001.json
{
  "id": "card_test_001",
  "name": "Test-Minion",
  "cost": 2,
  "attack": 2,
  "health": 1,
  "keywords": ["TAUNT"],
  "text": "Has Taunt.",
  "rarity": "COMMON"
}
```

---

## 10. Akzeptanztests (Definition of Done)

### Phase 1 Done Kriterien
- [ ] `pytest` läuft mit Erfolg
- [ ] Coverage > 80% für `core/engine` und `core/cards`
- [ ] Unit Tests für alle neuen Funktionen
- [ ] No regressions von vorherigem Tag

### Phase 2 Done Kriterien
- [ ] E2E: Komplette Partie gegen AI spielbar
- [ ] Kampagnen-Mission funktional (Start bis Ende)
- [ ] Belohnungen korrekt verteilt
- [ ] Keine Crashs bei Edge Cases (leeres Deck, max Mana, etc.)

### Phase 3 Done Kriterien
- [ ] PvP Matchmaking funktioniert (mind. 5 Partien)
- [ ] Gilden-Operationen (Gründung, Beitritt)
- [ ] Raid kooperativ (2-4 Spieler Test)
- [ ] Replay-System erstellt verwertbare Dateien

### Phase 4 Done Kriterien
- [ ] Android Build installierbar
- [ ] UI auf 3 Geräte-Klassen getestet (Phone, Tablet, Desktop)
- [ ] Performance: Keine Memory Leaks, FPS stabil
- [ ] Accessibility Basics (Farbenkontrast, Focus Order)

---

## 11. Bug Report Format (wenn an Sub-Agenten gemeldet)

```markdown
## Bug Description
[Kurze Beschreibung des Problems]

## Steps to Reproduce
1. Schritt 1
2. Schritt 2
3. Schritt 3

## Expected Behavior
[Was passieren sollte]

## Actual Behavior
[Was tatsächlich passiert]

## Environment
- OS: Windows 11
- Python: 3.11.4
- Flet: 0.20.0
- Game Version: 1.0.0

## Screenshots/Logs
[Fehler-Logs, Screenshots angehängt]

## Test Status
- [ ] Reproduzierbar
- [ ] Nicht reproduzierbar
- [ ] Intermittierend (schätzt Häufigkeit)
```

---

## 12. Offene Test-Fragen

- [ ] **Test-Daten-Management:** Fixtures im Repo oder generiert?
- [ ] **CI Runner:** GitHub Actions Self-Hosted vs. Gehostet?
- [ ] **Browser Support:** Chromium only oder auch Firefox/Safari?
- [ ] **Flet Version:** Stable nehmen oder Nightly für neue Features?
- [ ] **Property-Based Testing:** Hypothesis übernehmen oder Classic Unit Tests?

---

*Dokument-Version: 1.0*  
*Status: Foundation Phase*  
*Erstellt: 2026-10-03*