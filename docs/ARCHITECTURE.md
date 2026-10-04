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
| **core/engine** | Game State Machine, Match-Lifecycle, Rules Engine | CODE_ARCHITECT |
| **core/cards** | Kartendefinitionen, Registry, Effect System | CODE_ARCHITECT + CODE_IMPLEMENTOR |
| **core/pve** | PvE-Gegner, KI-Heuristiken, Boss-Phasen, Begegnungen | CODE_ARCHITECT + TEST_ENGINEER |
| **core/world** | Weltkarte, Regionen, Städte, Reiserouten, Standort | CODE_ARCHITECT |
| **core/economy** | Inventar, Händler, Güter, Währungen, Transaktionen | CODE_ARCHITECT + CODE_IMPLEMENTOR |
| **core/professions** | Berufe, Rezepte, Rohstoffe, Crafting-Engine | CODE_ARCHITECT + CODE_IMPLEMENTOR |
| **core/quests** | Story-Kapitel, Haupt-/Nebenquests, Questlog, Dialoge | CODE_ARCHITECT |
| **core/storage** | Versioniertes Savegame-System, Migrationen, Atomares Speichern | CODE_ARCHITECT + DATABASE_SPECIALIST |
| **client/** | Flet UI (GameBoard, Map, Städte, Deckbau, Inventar, Crafting) | FRONTEND_SPECIALIST |
| **tools/** | Card Editor, Balance Tools, Content-Generatoren | CODE_ARCHITECT |
| **llm/integration** | Lokale LLM-Integration via Ollama (Strategie + Companion) | CODE_ARCHITECT |

### 1.3 Datenfluss
1. **User Input** → Flet UI Events
2. **Validation** → core/engine Rules Check
3. **State Update** → core/engine State Machine & Match Manager
4. **Rendering** → Flet UI Refresh
5. **Persistence** → core/storage (Sichere Spielstand-Aktualisierung bei Meilensteinen/Transaktionen)
6. **LLM Advisory** → Strategy-Agent (Qwen3 4B) schlägt Zug vor → Regel-Engine validiert Legalität → Spiel führt Zug aus
7. **LLM Companion** → Companion-LLM (Llama 3.2 3B) konversiert mit Spieler, erklärt Züge

### 1.4 Entscheidungs-Prinzipien
- **Deterministische Engine:** Alle Spiellogik im Client, Replays möglich durch exakte Zustandswiederholung
- **Data-Driven:** Karten, Rezepte, Quests, Händlerangebote und Encounters in JSON/YAML
- **Separation of Concerns:** UI getrennt von Geschäftslogik
- **Persistenter Kampagnen-Fortschritt:** Kein Permadeath, Niederlagen beschädigen niemals den Spielstand, Kämpfe beliebig wiederholbar
- **Testbarkeit:** Jedes Modul hat automatisierte Unit- & Integrationstests
- **LLM Integration:** Game State wird strukturiert als JSON an lokale Ollama-LLMs übergeben; Engine behält absolute Autorität über Spielablauf

---

## 2. Modul-Detail-Design

### 2.1 core/engine - Game State Machine & Match-Lifecycle
**Zustände (Phasen):**
```
MULLIGAN → TURN_START → DRAW → MAIN_PHASE → COMBAT → TURN_END → NEXT_TURN → GAME_OVER (VICTORY / DEFEAT)
```

**Events (nicht-exhaustiv):**
- `on_card_played`
- `on_minion_summoned`
- `on_minion_died`
- `on_damage_dealt`
- `on_hero_power_used`
- `on_turn_start`
- `on_turn_end`
- `on_game_end` (Übergabe von Belohnungen bei Sieg; Retry-Option bei Niederlage)

**Pattern:** Event-Driven mit Observer-Pattern für UI Updates

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

**Effect System (kompositionsbasiert):**
- Effects werden zur Runtime angewandt
- Keine tiefen Vererbungsbäume
- Effect-Chain möglich (z. B. Battlecry → Deathrattle)

### 2.3 core/pve - PvE-Engine & KI
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
  enrage_timer: 180  # Runden/Sekunden bis Enrage
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
- Regelkonforme Aktionsauswahl (Legale Aktionen filtern, Board-Bewertung, Mana-Effizienz, Face-Damage)
- Optionale Strategy-LLM-Anbindung (Qwen3 4B) für fortgeschrittene Züge
- Skriptbare Boss-Phasen und Verhaltensmuster

### 2.4 core/world, core/economy & core/professions
**Welt & Städte (`core/world`):**
- Regionen mit verbundenen Städten und Routen
- Freischaltung über Story-Fortschritt
- Bereisbar ohne Permadeath-Verlust

**Wirtschaft & Handel (`core/economy`):**
- Inventar mit Stapelmengen für Rohstoffe, Verbrauchsgüter und Handelswaren
- Händler mit regionalen Preisunterschieden und dynamischen/festen Beständen
- Atomare Transaktionen (Guthaben, Items, Karten)

**Berufe & Crafting (`core/professions`):**
- Berufsfortschritt mit Erfahrung (XP) und Stufen
- Rezepte mit Zutaten, Werkstattanforderungen und Ergebnissen
- Transaktionssichere Herstellung (Materialverbrauch, Output, XP)

### 2.5 core/storage - Versioniertes Speichersystem
- Speicherung des vollständigen Fortschritts (Sammlung, Decks, Inventar, Gold, Quests, Standort, Berufe)
- Versioniertes Schema mit automatischen Migrationspfaden
- Atomares Schreiben (Safe Save / Temp-File Swap) gegen Datenverlust

---

## 3. Technologie-Entscheidungen

### 3.1 Sprache & Runtime
- **Python 3.11+** (typisiert mit type hints)

### 3.2 UI Framework
- **Flet** (Flutter-basiert)
- **Warum Flet?** Cross-Platform (Desktop/Web/Android), Single Codebase, native Python-Integration
- **Responsive Design:** `page.window_width` basierte Layouts

### 3.3 Datenpersistenz
- **JSON / SQLite** für lokale Speicherung
- Versioniertes Savegame mit Migrations-Layer
- **JSON / YAML** für Kartendaten, Rezepte, Dialoge und Encounter-Scripts

### 3.4 LLM Integration (Lokal via Ollama)
- **Strategie:** Qwen3 4B (JSON output, strikte Auswahl legaler Züge)
- **Companion:** Llama 3.2 3B (Rollenspiel, Erklärungen, Chat)
- Lokale REST-Schnittstelle `http://127.0.0.1:11434/api/chat`

### 3.5 Testing Strategy
- **Unit Tests:** pytest für core/engine, core/cards, core/pve, core/storage, core/economy, core/professions
- **Integration Tests:** Vollständige Partien, Save/Load-Zyklen, Handels- & Crafting-Transaktionen
- **Replay Validation:** Deterministische Zustandswiederholung

---

## 4. Entwicklungs-Workflow

### 4.1 Branch-Strategie
```
main:   Production-ready Code
dev:    Integrierender Entwicklungszweig
feature/*: Feature-Arbeitszweige (kurzlebig)
hotfix/*: Produktive Bugfixes
```

### 4.2 Commit-Konventionen
```
feat:     Neue Funktion
fix:      Bugbehebung
docs:     Dokumentationsänderungen
style:    Formatierung
refactor: Code-Refactoring (keine Funktionsänderung)
test:     Hinzufügen von Tests
chore:    Nicht-quellcode Änderungen
```

### 4.3 Pull Request Regeln
- **Template ausfüllen:** Description, Testing, Screenshots (wenn UI)
- **Minimum 1 CODE_REVIEWER** Approval
- **Kein Merge** bei fehlgeschlagenen Tests
- **Changelog automatisch** generieren (conventional commits)

---

## 5. Meilensteine (gemäß ROADMAP.md)

| Meilenstein | Spielbarer Umfang |
|-------------|-------------------|
| **Kampfprototyp** | Vollständiger PvE-Kampf mit Wiederholungsoption und verlässlichen Regeln. |
| **Persistenz-Prototyp** | Sammlung, Deckbau, Inventar, Guthaben und Speichern/Laden bilden einen dauerhaften Fortschrittskreislauf. |
| **Story-Vertical-Slice** | Ein Story-Abschnitt, zwei Städte, eine verbindende Weltkartenroute, Warenhandel, Stadtaktivitäten und ein Beruf mit Crafting. |
| **Alpha** | Zentrale Kampagnen-, Weltkarten-, Stadt-, Handels- und Berufssysteme integriert; Inhaltsausbau. |
| **Beta** | Geplanter Story-Umfang spielbar; Fokus auf Balance, Wirtschaft, UI und Savegame-Stabilität. |
| **Release** | Getestete Kampagne mit mehreren Städten, Weltkarte, Warenhandel und Berufssystem samt Crafting. |

---

*Dokument-Version: 1.1*  
*Status: Foundation Phase*  
*Zuletzt aktualisiert: 2026-10-04*