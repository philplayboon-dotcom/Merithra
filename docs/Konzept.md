# Merithra - Kartenspiel Konzept

## 1. Projektübersicht

**Projektname:** Merithra  
**Genre:** Digitales Sammelkartenspiel (CCG/TCG)  
**Fokus:** PvE-lastig (Raids, Dungeons, Kampagne) mit optionalen PvP- und Gilden-Features  
**Tech-Stack:** Python 3.11+, Flet (Flutter-basiert, für Desktop/Web/Android)  
**Zielplattformen:** Windows, Linux, macOS, Web, Android (später)  
**Architektur:** Client-Server (später), initial Local-First mit Offline-Support  

---

## 2. Kernspielmechaniken

### 2.1 Grundregeln (Hearthstone-ähnlich)

| Aspekt | Beschreibung |
|--------|--------------|
| **Lebenspunkte** | 30 HP pro Spieler/Helden |
| **Mana-System** | 1 Mana pro Runde (max 10), keine Mana-Kristalle als Karten |
| **Kartenarten** | Diener, Zauber, Waffen, Orte, Heldenkräfte |
| **Klassen** | 8+ spielbare Klassen mit einzigartigen Heldenkräften |
| **Deckgröße** | 30 Karten (max 2× gleiche Karte, 1× legendär) |
| **Zugstruktur** | Karte ziehen → Mana auffrischen → Spielen/Angreifen → Zug beenden |

### 2.2 PvE-spezifische Erweiterungen

#### **Begegnungs-Mechaniken**
- **Boss-Mechaniken:** Phasen, Enrage-Timer, spezielle Boss-Kräfte
- **Umgebungs-Effekte:** „Stürmisch“ (Windfury für alle), „Verflucht“ (Schaden bei Kartenziehen)
- **Scenario-Ziele:** „Überlebe 10 Runden“, „Zerstöre 3 Totems“, „Schütze NPC“
- **Belohnungstabellen:** Beute basierend auf Leistung (Zeit, HP-Verlust, Ziele)

#### **Fortschrittssysteme**
- **Kampagnen-Modus:** Kapitel mit verzweigten Pfaden, Story-Entscheidungen
- **Abenteuer-Modus:** Roguelike-Runs (Draft + Artefakte + Boss-Rush)
- **Tages-/Wochen-Herausforderungen:** Modifier-Runs für Cosmetics/Währung
- **Ruf-System:** Fraktions-Ruf schaltet Karten, Helden, Kosmetik frei

---

## 3. PvE-Inhalte

### 3.1 Kampagne (Story-Modus)
- **8+ Kapitel** pro Klasse, verzweigte Narrative
- **Boss-Begegnungen** mit einzigartigen Decks/Mechaniken
- **Zwischen-Sequenzen:** Dialoge, Entscheidungen (einfluss auf Belohnungen)
- **Neues Spiel+:** Erhöhte Schwierigkeit, neue Belohnungen

### 3.2 Raids (Kooperativ, 1-4 Spieler)
| Feature | Beschreibung |
|---------|--------------|
| **Boss-Phasen** | 3-5 Phasen mit wechselnden Mechaniken |
| **Shared HP Pool** | Gruppe teilt sich Lebenspunkte (skaliert mit Spielern) |
| **Koordinations-Mechaniken** | „Teilt Schaden auf“, „Kombiniert Zauber“, „Buff-Weitergabe“ |
| **Loot-System** | Personal Loot + Gruppen-Bonus-Chest |
| **Schwierigkeiten** | Normal → Heroisch → Mythisch (wöchentlicher Lockout) |
| **Raids pro Erweiterung** | 1 Großer Raid (6-8 Bosse) + 2 Mini-Raids (2-3 Bosse) |

### 3.3 Dungeons (1-3 Spieler, kürzer)
- **Laufzeit:** 15-30 Min
- **Zufällige Modifikatoren** (Affixe: „Explosiv“, „Verstärkt“, „Tyrannisch“)
- **Schlüssel-System:** Dungeon-Schlüssel droppen in Welt/Kampagne
- **Endlos-Modus:** Skalierende Wellen für Highscore/Leaderboards

### 3.4 Welt-Events & Weltbosse
- **Zeitgesteuerte Events** (alle 2-4 Stunden)
- **Offene Welt-Zonen** mit gemeinsamen Fortschrittsbalken
- **Weltbosse** erfordern 10-20 Spieler (Skalierung)
- **Belohnungen:** Exklusive Kosmetik, Materialien, Titel

---

## 4. Gilden-System

### 4.1 Gilden-Features
| Feature | Beschreibung |
|---------|--------------|
| **Gilden-Level** | XP durch Aktivitäten → Perks (Gold+, XP+, Slots+) |
| **Gildenbank** | Gemeinsame Ressourcen, Karten-Leihsystem |
| **Gilden-Raids** | Wöchentlicher Termin, gemeinsamer Fortschritt |
| **Gilden-Kriege** | PvE-Wettbewerb: „Wer tötet Boss X schneller?“ |
| **Gilden-Questboard** | Tägliche/Wöchentliche Gruppenaufgaben |
| **Offizier-Rollen** | Rekrutierung, Bank, Events, Diplomatie |
| **Gilden-Halle** | Anpassbarer sozialer Hub (Kosmetik, Trophäen) |

### 4.2 Gilden-Fortschritt
- **Saisonale Gilden-Ranglisten** (PvE-Score)
- **Exklusive Belohnungen:** Rückseiten, Titel, Mounts, Helden-Skins
- **Catch-Up-Mechanik** für neue/ kleine Gilden

---

## 5. PvP-Modus (Sekundär)

### 5.1 Formate
| Modus | Beschreibung |
|-------|--------------|
| **Ranglistenspiel** | Standard (aktuell), Wild (alle Karten), Twist (rotierend) |
| **Arena/Draft** | 30 Karten draften → 12 Siege / 3 Niederlagen |
| **Turniere** | In-Game Bracket, Spectator-Mode, Preisgeld-Pool |
| **Freundschaftsspiele** | Direkte Herausforderung, benutzerdefinierte Regeln |

### 5.2 PvP-Balance-Philosophie
- **Getrennte Balancing-Patches** für PvE vs PvP (Karten können unterschiedliche Werte haben)
- **PvP-spezifische Keywords** (z. B. „PvP: Wirkt nur gegen Spieler“)
- **Kein Pay-to-Win:** Alle Karten spielbar erspielbar

---

## 6. Wirtschaft & Progression

### 6.1 Währungen
| Währung | Quelle | Verwendung |
|---------|--------|------------|
| **Gold** | Quests, Siege, Dungeons | Packs, Arena-Eintritt, Händler |
| **Staub/Asche** | Kartenzersetzung | Karten-Crafting |
| **Runen/Edelsteine** | Raids, High-End PvE | Kosmetik, legendäre Upgrades |
| **Gilden-Marken** | Gilden-Aktivitäten | Gilden-Shop, Halle-Upgrades |
| **Ehren-Medaillen** | PvP, Turniere | PvP-Kosmetik, Titel |

### 6.2 Monetarisierung (Fair Play)
- **Keine Lootboxen** → Direkter Kauf: Packs, Skins, Kampagnen
- **Battle Pass** (kosmetisch only, kein Power)
- **Erweiterungen** als DLC (neue Karten, PvE-Inhalt)
- **Alle spielrelevanten Inhalte** free-to-play erspielbar

---

## 7. Technische Architektur

### 7.1 High-Level Struktur
```
merithra/
├── core/                    # Spiellogik (framework-agnostisch)
│   ├── engine/             # Game Engine (State Machine, Rules)
│   ├── cards/              # Kartendefinitionen, Registry
│   ├── entities/           # Player, Hero, Minion, Spell, Weapon
│   ├── mechanics/          # Keywords, Effects, Triggers
│   ├── pve/                # Encounter, Boss, Dungeon, Raid Logic
│   ├── guild/              # Guild System
│   ├── progression/        # XP, Reputation, Collections
│   └── networking/         # Protocol, Messages (für später)
├── server/                 # Dedicated Server (später)
│   ├── api/                # REST/gRPC Endpoints
│   ├── matchmaking/        # PvP, Raid, Dungeon Queue
│   ├── persistence/        # DB Models, Migrations
│   └── events/             # Seasonal Events, World Bosses
├── client/                 # Flet UI
│   ├── screens/            # MainMenu, DeckBuilder, GameBoard, ...
│   ├── components/         # Reusable UI (CardWidget, ManaCrystal, ...)
│   ├── state/              # Client State Management
│   ├── assets/             # Images, Sounds, Animations
│   └── utils/              # Helpers, Theme, Localization
├── shared/                 # Shared Types, Protocols, Constants
├── tools/                  # Card Editor, Balance Tools, Data Pipeline
├── tests/                  # Unit, Integration, E2E
└── docs/                   # Architecture, API, Design Docs
```

### 7.2 Kern-Module (core/)

#### **Engine (State Machine)**
```python
# Phasen: MULLIGAN -> TURN_START -> DRAW -> MAIN_PHASE -> COMBAT -> TURN_END -> NEXT_TURN
# Event-System: on_play, on_death, on_damage, on_heal, on_turn_start, ...
# Deterministisch für Replays/Tests
```

#### **Karten-System**
- **Datengesteuert:** JSON/YAML Definitionen → Python-Klassen zur Runtime
- **Effect-System:** Kompositions-basiert (nicht Vererbung)
- **Keywords:** Taunt, Charge, Divine Shield, Poisonous, Lifesteal, Rush, Windfury, Reborn, Deathrattle, Battlecry, Spellburst, Corrupt, Tradeable, Discover, Choose One, Twinspell, Echo, Overload, Quest, Sidequest, Objective

#### **PvE-Engine**
- **Encounter-Scripting:** YAML/JSON für Boss-Verhalten (nicht Hardcode)
- **AI-System:** Verhaltensbäume (Behavior Trees) für Bosses
- **Difficulty Scaling:** Parameter-basiert (HP, Damage, Extra-Karten, Mechaniken)

### 7.3 Felt UI Architektur

#### **Screen-Flow**
```
MainMenu → [Campaign | Raids | Dungeons | PvP | Guild | Collection | Shop]
    │
    ├── Campaign → ChapterSelect → MissionSelect → GameBoard
    ├── Raids → RaidLobby (Matchmaking) → GameBoard (Multiplayer)
    ├── Dungeons → DungeonSelect → KeyConfirm → GameBoard
    ├── PvP → ModeSelect → Queue → GameBoard
    ├── Guild → GuildHall → [Roster | Bank | Quests | Raid | Hall]
    └── Collection → DeckBuilder / CardLibrary / Crafting
```

#### **GameBoard Komponenten**
- **Board-Zonen:** Hand, Board (7 Slots), Hero, Weapon, Hero Power, Deck, Graveyard, Secrets
- **Drag & Drop:** Karte spielen, Angreifen (Ziel-Auswahl)
- **Animationen:** Zeichnen, Spielen, Angreifen, Tod, Buff/Debuff
- **Tooltips:** Karte inspektion, Keyword-Erklärungen
- **Responsive:** Desktop (16:9), Tablet, Mobile (Hochformat-Anpassung)

#### **Theming & Accessibility**
- **Design System:** Farben, Spacing, Typography, Shadows als Theme-Klasse
- **Dark/Light Mode** + High Contrast
- **Screen Reader** Support (Semantische Labels)
- **Skalierbare UI** (Flet `page.window_width` responsive)

---

## 8. Datenmodell (Übersicht)

### 8.1 Kern-Entitäten
```python
# Card
id: str
name: str
card_type: CardType (MINION, SPELL, WEAPON, LOCATION, HERO_POWER)
class_type: ClassType (NEUTRAL, WARRIOR, MAGE, ...)
rarity: Rarity (FREE, COMMON, RARE, EPIC, LEGENDARY)
cost: int
attack: int | None
health: int | None
durability: int | None
keywords: list[Keyword]
text: str # Rohtext für Anzeige
effects: list[Effect] # Strukturiert für Engine
artist: str
set_id: str
collectible: bool

# Player (in Game)
hero: Hero
hero_power: HeroPower
deck: list[Card]
hand: list[Card]
board: list[Minion] # max 7
graveyard: list[Card]
secrets: list[Secret]
mana: int
max_mana: int
armor: int
fatigue: int

# Encounter (PvE)
boss: BossEntity
phases: list[BossPhase]
environment_effects: list[Effect]
objectives: list[Objective]
rewards: RewardTable
```

---

## 9. Entwicklungs-Phasen

### Phase 1: Foundation (MVP - Local Only)
- [ ] Core Engine: State Machine, Rules, Card System
- [ ] 50+ Basis-Karten (Neutral + 3 Klassen)
- [ ] Singleplayer vs AI (einfache KI)
- [ ] Flet GameBoard: Hand, Board, Hero, Mana, Zugende
- [ ] Deck Builder (30 Karten, Validierung)
- [ ] Lokale Speicherung (SQLite/JSON)

### Phase 2: PvE Content
- [ ] Kampagnen-Framework (Kapitel, Missionen, Dialoge)
- [ ] Boss-Mechaniken & AI (Behavior Trees)
- [ ] 1. Kapitel pro Klasse (3 Bosse each)
- [ ] Belohnungssystem (Gold, Karten, XP)
- [ ] Abenteuer-Modus (Roguelike: Draft + Artefakte)

### Phase 3: Multiplayer & Social
- [ ] Netzwerk-Protokoll (WebSocket/gRPC)
- [ ] Dedicated Server (Matchmaking, State Sync)
- [ ] PvP: Rangliste, Arena, Freundschaftsspiele
- [ ] Gilden-System (Erstellung, Chat, Bank, Perks)
- [ ] Raids: Koop-Lobby, Shared State, Boss-Sync

### Phase 4: Live-Ops & Polish
- [ ] Saison-System (Battle Pass, Ranglisten-Reset)
- [ ] Events: Weltbosse, Feiertags-Events
- [ ] Mobile-Optimierung (Touch, Hochformat, Performance)
- [ ] Accessibility & Localization (DE/EN mindestens)
- [ ] Anti-Cheat, Replay-System, Spectator Mode

### Phase 5: Erweiterungen
- [ ] Neue Karten-Sets (alle 3-4 Monate)
- [ ] Neue Klassen / Helden-Skins
- [ ] Neue PvE-Modi (Tower Defense, Puzzle, Coop-Campaign)
- [ ] Modding-Support (Custom Cards, Adventures)

---

## 10. Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Flet Mobile Performance | Mittel | Hoch | Early Prototyping, Profiling, Fallback auf WebView |
| PvE Balance (zu einfach/schwer) | Hoch | Mittel | Telemetrie, Parameter-gesteuerte Difficulty, Beta-Tests |
| Multiplayer Sync (Desync) | Mittel | Hoch | Deterministische Engine, Server-Authoritative, Replay-Validation |
| Scope Creep (Features) | Hoch | Hoch | Phasen-Plan, "Nein" zu Non-MVP Features, Regular Reviews |
| Kartendaten-Pflege | Mittel | Mittel | Data-Driven Tools, Card Editor, Automated Tests |
| KI für PvE | Mittel | Mittel | Behavior Trees, Scripting, nicht ML (vorhersehbar) |
| LLM-Integration | Mittel | Mittel | Klare Prompt-Profile, striktes JSON-Format für Strategy, Safety-Checks für Companion |

---

## 10. Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Flet Mobile Performance | Mittel | Hoch | Early Prototyping, Profiling, Fallback auf WebView |
| PvE Balance (zu einfach/schwer) | Hoch | Mittel | Telemetrie, Parameter-gesteuerte Difficulty, Beta-Tests |
| Multiplayer Sync (Desync) | Mittel | Hoch | Deterministische Engine, Server-Authoritative, Replay-Validation |
| Scope Creep (Features) | Hoch | Hoch | Phasen-Plan, "Nein" zu Non-MVP Features, Regular Reviews |
| Kartendaten-Pflege | Mittel | Mittel | Data-Driven Tools, Card Editor, Automated Tests |
| KI für PvE | Mittel | Mittel | Behavior Trees, Scripting, nicht ML (vorhersehbar) |
| LLM-Integration | Mittel | Mittel | Klare Prompt-Profile, striktes JSON-Format für Strategy, Safety-Checks für Companion |

## 11. KI-Integration (LLM Tutor & Strategie)

### 11.1 Strategie-Agent (Qwen3 4B Q4_K_M)
- Übernimmt Spielzug-Vorschläge und Board-Bewertung
- Gibt strukturiertes JSON mit Aktion und Ziel aus
- Sieht nur legalen Aktionen und öffentlichen Spielzustand
- Temperatur: 0.2 bis 0.4 für konsistente, vorhersehbare Entscheidungen
- bleibt außerhalb der autoritativen Spiellogik

### 11.2 Companion-LLM (Llama 3.2 3B Q4)
- Führt Konversationen mit dem Spieler
- Erklärt Züge, gibt Tipps, verkörpert Spielfigur
- Darf keine verdeckten Karten, Gegner-Handkarten oder RNG-Werte sehen
- Temperatur: 0.6 bis 0.8 für natürlichere Konversation
- Persönlichkeit: Sarkastisch, hilfsbereit, als Kartenmeister "Rook"

### 11.3 Entwicklung
- Während der Entwicklung: lokale Ollama-Installation
- Modelle: `qwen3:4b` für Strategie, `llama3.2:3b` für Konversation
- Alle Requests über `http://127.0.0.1:11434/api/chat`
- Keine API-Kosten, keine Anfragelimits

### 11.4 Spätere Cloud-Option
- DeepSeek V3 über OpenRouter als optionalem Cloud-Provider
- Lokale Ollama-Installation bleibt als Fallback erhalten
- Spiel muss weiterhin ohne Account, API-Key und Internet funktionieren

---

## 12. Offene Entscheidungen (für Architekt)

- [ ] **Server-Tech:** Python (FastAPI + WebSockets) vs Go vs Node.js?
- [ ] **Datenbank:** PostgreSQL (relational) vs MongoDB (flexibel) vs SQLite (embedded für Client)?
- [ ] **Asset-Pipeline:** Wie werden Karten-Arts/Animationen verwaltet? (Spine? Rive? PNG-Sequenzen?)
- [ ] **KI-Approach:** Behavior Trees (Python) vs Lua-Scripting vs Godot-Style Visual Scripting?
- [ ] **Cross-Platform Sync:** Account-System (E-Mail, Steam, Google, Apple) oder anonym/local-first?
- [ ] **Cheat-Schutz:** Wie viel Server-Authoritative vs Client-Trust bei PvE?

---

## 13. Nächste Schritte

1. **CODE_ARCHITECT** → Technisches Design (Module, Interfaces, Data Flow)
2. **DATABASE_SPECIALIST** → Schema für Accounts, Collection, Progression, Guilds
3. **CODE_IMPLEMENTOR** → Core Engine Prototyp (State Machine, Card System)
4. **FRONTEND_SPECIALIST** → Flet GameBoard MVP (Drag-Drop, Zonen, Animationen)
5. **TEST_ENGINEER** → Test-Strategie (Engine Unit Tests, Integration, Replay)
6. **SECURITY_AUDITOR** → Threat Model für Multiplayer/Account-System

---

*Dokument-Version: 1.0*  
*Erstellt: 2026-10-03*  
*Status: Entwurf zur Review*