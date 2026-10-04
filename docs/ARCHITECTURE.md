# Merithra - Architektur-Dokument

## Versionsverwaltung
- **Version:** 1.0 (Foundation Phase)
- **Status:** Entwurf
- **Zuletzt aktualisiert:** 2026-10-03

---

## 1. High-Level Architektur

### 1.1 Schichten-Modell
```
+---------------------+        +---------------------+
|    Presentation     | <----> |     Application     |
|   (Flet UI)         |        |   (Python Core)     |
+---------------------+        +---------------------+
          ^                           ^
          |                           |
          |                           v
          |                   +---------------------+
          +------------------> |   Database/Storage  |
                            |  (SQLite/PostgreSQL)|
                            +---------------------+
```

### 1.2 Kern-Komponenten
| Modul | Beschreibung | Zuständigkeit |
|-------|--------------|---------------|
| **core/engine** | Game State Machine, Rules Engine | CODE_ARCHITECT |
| **core/cards** | Kartendefinitionen, Registry, Effects | CODE_ARCHITECT + CODE_IMPLEMENTOR |
| **core/pve** | Encounter System, Boss AI, Phases | CODE_ARCHITECT + TEST_ENGINEER |
| **core/guild** | Guild System, Bank, Ranks | CODE_ARCHITECT |
| **core/progression** | XP, Reputation, Collections | CODE_ARCHITECT |
| **client/flet** | UI Komponenten, Screen Management | FRONTEND_SPECIALIST |
| **server/** | Networking, Matchmaking, State Sync | DEVOPS_ENGINEER (später) |
| **tools/** | Card Editor, Balance Tools | CODE_ARCHITECT |
| **llm/integration** | Local LLM Integration via Ollama (Strategy + Companion) | CODE_ARCHITECT |

### 1.3 Datenfluss
1. **User Input** → Flet UI Events
2. **Validation** → core/engine Rules Check
3. **State Update** → core/engine State Machine
4. **Rendering** → Flet UI Refresh
5. **Network** (später) → Server ↔ Client Sync
6. **LLM Advisory** → Strategy-Agent (Qwen3 4B) schlägt Zug vor → Regel-Engine validiert Legalität → Spiel führt Zug aus
7. **LLM Companion** → Companion-LLM (Llama 3.2 3B) konvertiert mit Spieler, erklärt Züge

### 1.4 Entscheidungs-Prinzipien
- **Deterministische Engine:** Alle Spiellogik im Client, Replays möglich durch exakte Zustandswiederholung
- **Data-Driven:** Karten und Encounters in JSON/YAML, nicht Hardcode
- **Separation of Concerns:** UI getrennt von Geschäftslogik
- **Testbarkeit:** Jedes Modul hat Unit-Tests
- **LLM Integration:** Game State wird strukturiert als JSON an lokale Ollama-LLMs übergeben; Engine behält absolute Autorität über Spielablauf

---

## 2. Modul-Detail-Design

### 2.1 core/engine - Game State Machine
**Zustände (Phasen):**
```
MULLIGAN → TURN_START → DRAW → MAIN_PHASE → COMBAT → TURN_END → NEXT_TURN
```

**Events (nicht-exhaustiv):**
- `on_card_played`
- `on_minion_summoned`
- `on_minion_died`
- `on_damage_dealt`
- `on_hero_power_used`
- `on_turn_start`
- `on_turn_end`
- `on_game_end`

**Pattern:** Event-Driven mit observer Pattern für UI Updates

### 2.2 core/cards - Kartensystem
**Definition Format (JSON/YAML Beispiel):**
```yaml
id: "card_001"
name: "Feuerball"
cost: 3
card_type: SPELL
class_type: NEUTRAL
rarity: COMMON
targets: [HERO, MINION]
effects:
  - type: DAMAGE
    target_filter: ANY
    value: 6
keywords: [None]
text: "Verursache 6 Schaden."
```

**Effect System (kompositionbasiert):**
- Effects werden zur Runtime angewandt
- Keine tiefen Vererbungsbäume
- Effect-Chain möglich (z. B. Battlecry → Deathrattle)

### 2.3 core/pve - PvE-Engine
**Encounter Scripting (YAML Beispiel):**
```yaml
encounter_id: "boss_brambol"
name: "Brontalos, der Brenner"
phase_count: 3

phase_1:
  hp: 50
  abilities:
    - FIREBALL_RANDOM
    - SPAWN_MINIONS

phase_2:
  hp: 30
  enrage_timer: 180  # Sekunden bis Enrage
  abilities:
    - OVERLOAD
    - BERSERK

phase_3:
  hp: 20
  abilities:
    - MULTI_TARGET
    - SUMMON_ELEMENTALS
```

**AI-System:**
- Behavior Trees (Python-basiert)
- Scripted Patterns für Standard-Bosse
- Parameter-gesteuerte Schwierigkeit (HP, Damage, Mechaniken)

### 2.4 core/guild - Gilden-System
**Datenmodell:**
- Guild: id, name, level, xp, perks, officer_roles
- Member: id, name, rank, contribution, last_online
- Bank: items, gold, cards_loaned

**Workflow:**
1. Player creates/joins guild
2. Guild activities → XP → Level up
3. Perks unlocked (Gold+, Card Slots+, Raid Bonus+)
4. Weekly Raid scheduling
5. Guild Wars (PvE competition)

---

## 3. Technologie-Entscheidungen

### 3.1 Sprache & Runtime
- **Python 3.11+** (typisiert mit type hints)
- **Performance-critical:** Optional Cython oder NumPy für schwere Berechnungen

### 3.2 UI Framework
- **Flet** (Flutter-basiert)
- **Warum Flet?** Cross-Platform (Desktop/Web/Android), Single Codebase, guter Python-Integrations
- **Responsive Design:** `page.window_width` basierende Layouts

### 3.3 Datenpersistenz (MVP)
- **SQLite** für lokale Client-Speicherung
- **JSON** für Kartendaten und Encounter-Scripts
- **Geplante Migration** auf PostgreSQL bei Server-Implementation

### 3.4 Zukunft Server-Technologie
- **Option A:** FastAPI + WebSockets (Python-Ökosystem konsistent)
- **Option B:** Go + gRPC (Performance- Fokus)
- **Entscheidung:** Zur Phase 3 (Multiplayer) treffen

### 3.5 Testing Strategy
- **Unit Tests:** pytest für core/engine, core/cards
- **Integration Tests:** Complete game flows
- **Replay Validation:** Deterministic state reproduction
- **Performance Tests:** Flet UI frame rates

---

## 4. Entwicklungs-Workflow

### 4.1 Branch-Strategie
```
main:   Production-ready Code
dev:    Integrierende Entwicklungszweig
feature/*: Feature-Arbeitszweige (kurzlebig)
hotfix/*: Produktsche Bugs
```

### 4.2 Commit-Konventionen
```
feat:     Neue Funktion
fix:      Bugbehebung
docs:     Dokumentationsänderungen
style:    Formatierung, fehlende Semikolone
refactor: Code-Refactoring (keine Funktionsänderung)
test:     Hinzufügen von Tests
chore:    Nicht-quellcode Änderungen
```

### 4.3 Pull Request Regeln
- **Template ausfüllen:** Description, Testing, Screenshots (wenn UI)
- **Minimum 1 CODE_REVIEWER** approval
- **Kein Merge** bei fehlgeschlagenen Tests
- **Changelog automatisch** generieren (conventional commits)

### 4.4 Code Review Checkliste
- [ ] Architektur-Konzept befolgt
- [ ] Keine harten Code-Werte (alle in Config/JSON)
- [ ] Tooltips und Accessibility Labels vorhanden
- [ ] Keine Secrets im Code
- [ ] Performance-Auswirkung geprüft (bei signifikanten Änderungen)
- [ ] Tests vorhanden & laufen

---

## 5. Offene Architektur-Fragen

- [ ] **Kartendaten-Format:** JSON vs YAML vs Datenbank? (Entscheidung: JSON für Einfachheit)
- [ ] **AI-Implementierung:** Behavior Tree Library nutzen oder selbst implementieren?
- [ ] **Flet Version:** Stable vs Bleeding Edge nehmen?
- [ ] **Optimierung wann?** Erst ab 500+ simultanen Einheiten profilieren
- [ ] **Offline-First:** Vollständiges Spiel offline oder nur Basic Mode?

---

## 6. Nächste Meilensteine

| Meilenstein | Ziel | Fällig |
|-------------|------|-------|
| **M1** | Core Engine MVP (State Machine, basic card types) | Phase 1 |
| **M2** | Flet GameBoard prototyp (Hand, Board, Mana) | Phase 1 |
| **M3** | 10+ Basis-Karten implementiert | Phase 1 |
| **M4** | AI Simple Boss (1 Phase) | Phase 2 |
| **M5** | Kampagne Kapitel 1 (5 Missionen) | Phase 2 |
| **M6** | Gilden-System Grundgerüst | Phase 3 |
| **M7** | PvP Matchmaking Basic | Phase 3 |

---

*Dokument-Version: 1.0*  
*Status: Foundation Phase*  
*Erstellt: 2026-10-03*