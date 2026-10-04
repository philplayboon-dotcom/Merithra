# Merithra - Roadmap & Meilensteine

## Versionsverwaltung
- **Version:** 1.0
- **Status:** Planning Phase
- **Aktualisierungs-Rhythmus:** Quartalsweise + Monatsmeilensteine

---

## 1. Übersicht: Entwicklungsphasen

| Phase | Zeitraum | Fokus | Deliverables |
|-------|----------|-------|--------------|
| **Phase 1** | Okt - Dez 2026 | Foundation (MVP Local) | Core Engine, Basic UI, 10 Cards, LLM Integration (Strategie + Companion) |
| **Phase 2** | Jan - Mär 2027 | PvE Content | Kampagne, Raids, Dungeons, Progression |
| **Phase 3** | Apr - Jun 2027 | Multiplayer & Social | PvP, Gilden, Matchmaking, Netzwerk |
| **Phase 4** | Jul - Sep 2027 | Live-Ops & Polish | Seasonale Events, Mobile-Optimierung |
| **Phase 5** | Okt 2027+ | Erweiterungen | Neue Klassen, Sets, Modding-Support |

---

## 2. Phase 1: Foundation (MVP - Local Only)

### Ziele
- Spielbares Human vs AI
- Core Game Engine (State Machine, Rules)
- Flet UI: GameBoard, Deck Builder
- Lokale Speicherung (SQLite/JSON)

### Teil-Meilensteine

| Meilenstein | Beschreibung | Fertigstellung |
|-------------|--------------|----------------|
| **M1** | Core Engine: State Machine mit Phasen (MULLIGAN, TURN, etc.) | Woche 1-2 |
| **M2** | Karte spielen & Angreifen Mechanik | Woche 2-3 |
| **M3** | Flet GameBoard: Hand, Board, Hero, Mana Crystal | Woche 3-4 |
| **M4** | Deck Builder: 30 Karten limit, Validierung | Woche 4-5 |
| **M5** | 10+ Basis-Karten mit Keywords (Taunt, Charge, etc.) | Woche 5-6 |
| **M6** | Einfache KI: Spielzüge gemäß Regeln | Woche 6-7 |
| **M7** | LLM Integration: Strategie-Agent via Ollama (Qwen3 4B) | Woche 7-8 |
| **M8** | LLM Integration: Companion-LLM via Ollama (Llama 3.2 3B) | Woche 8-9 |
| **M9** | Unit Test Abdeckung > 80% für Engine | Woche 7-8 |
| **M10** | MVP Release: Spielbare Partie gegen KI | Ende Phase 1 |

### Success Criteria (Phase 1 Done)
- [ ] 1 Partie Human vs AI vollständig spielbar
- [ ] Alle Kern-Keywords implementiert (min. 5: Taunt, Charge, Divine Shield, Lifesteal, Windfury)
- [ ] Deck Builder erstellt valide Decks (30 Karten, max 2× non-legendary)
- [ ] UI flüssig (60 FPS Desktop, 30 FPS Web)
- [ ] Unit Tests bestehen (pytest)

---

## 3. Phase 2: PvE Content

### Ziele
- Vollständige Kampagne mit Story
- Raid- und Dungeon-System
- Progression & Belohnungssystem

### Teil-Meilensteine

| Meilenstein | Beschreibung | Fertigstellung |
|-------------|--------------|----------------|
| **M9** | Kampagnen-Framework: Kapitel & Missionen | Woche 1-2 |
| **M10** | 1. Kapitel pro Klasse (3 Bosse each) | Woche 2-3 |
| **M11** | Boss-Mechaniken & Phasen (3 Phasen pro Boss) | Woche 3-4 |
| **M12** | Behavior Trees für Boss AI | Woche 4-5 |
| **M13** | Belohnungssystem (Gold, Karten, XP) | Woche 5-6 |
| **M14** | Abenteuer-Modus (Roguelike Draft) | Woche 6-7 |
| **M15** | Fortschrittsspeicherung (Collection persist) | Woche 7-8 |
| **M16** | 1 vollständiger Playthrough (Kampagne + Abenteuer) | Ende Phase 2 |

### Success Criteria (Phase 2 Done)
- [ ] Kampagne spielbar (alle Kapitel, alle Klassen)
- [ ] 1 Raid (4 Spieler kooperativ) funktional getestet
- [ ] 1 Dungeon-Lauf (incl. Affixes) spielbar
- [ ] Belohnungen werden korrekt vergeben
- [ ] Abenteuer-Modus Randomness + Balance getestet

---

## 4. Phase 3: Multiplayer & Social

### Ziele
- PvP-Modi (Rangliste, Arena)
- Gilden-System (CRUD, Chat, Raids)
- Matchmaking & Netzwerk-Synchronisation

### Teil-Meilensteine

| Meilenstein | Beschreibung | Fertigstellung |
|-------------|--------------|----------------|
| **M17** | Netzwerk-Protokoll (WebSocket Design) | Woche 1-2 |
| **M18** | PvP Matchmaking (Queue System) | Woche 2-3 |
| **M19** | Ranglisten-System (Ladder) | Woche 3-4 |
| **M20** | Arena/Draft Modus | Woche 4-5 |
| **M21** | Gilden-Gründung & Bank-System | Woche 5-6 |
| **M22** | Gilden-Raid Kooperations-Modus | Woche 6-7 |
| **M23** | Chat & Offizier-Rollen | Woche 7-8 |
| **M24** | komplettes Multiplayer-Feature-Set | Ende Phase 3 |

### Success Criteria (Phase 3 Done)
- [ ] PvP Matchmaking funktioniert (LAN & Online Test)
- [ ] Arena-Run spielbar (30 Karten draften, 12 Siege/3 Niederlagen)
- [ ] Gilde erstellen, beitreten, verlassen funktioniert
- [ ] Gilden-Raid mit 4 Spielern kooperativ
- [ ] Chat-Nachrichten in Echtzeit

---

## 5. Phase 4: Live-Ops & Polish

### Ziele
- Mobile Optimierung (Android via Flet)
- Accessibility & Localization
- Saison-System & Events
- Performance-Optimierung

### Teil-Meilensteine

| Meilenstein | Beschreibung | Fertigstellung |
|-------------|--------------|----------------|
| **M25** | Touch-Optimierung & Hochformat-Layout | Woche 1-2 |
| **M26** | Dark Mode & High Contrast Theme | Woche 2-3 |
| **M27** | Lokalisierung: DE & EN | Woche 3-4 |
| **M28** | Performance-Profiling & Optimierung | Woche 4-5 |
| **M29** | Saison-Battle Pass System | Woche 5-6 |
| **M30** | Welt-Events & Welt-Bosse | Woche 6-7 |
| **M31** | Replay-System & Spectator Mode | Woche 7-8 |
| **M32** | Vollständige Android-Build-Test | Ende Phase 4 |

### Success Criteria (Phase 4 Done)
- [ ] Android-Build installierbar & spielbar
- [ ] UI auf Tablet/Mobile responsive & nutzbar
- [ ] Saison startet, Battle Pass vergeben Belohnungen
- [ ] Performance: Keine Memory Leaks nach 2h Spielzeit
- [ ] Replays können abgespielt & geteilt werden

---

## 6. Phase 5: Erweiterungen (Post-Launch)

### Ziele
- Kontinuierlicher Content-Zyklus
- Community-Feedback Implementation
- Modding-Support

### Roadmap-Themen

| Thema | Zeitplan | Beschreibung |
|-------|----------|--------------|
| **Karten-Sets** | Alle 3-4 Monate | Neue Karten, Mechaniken, Keywords |
| **Neue Klassen** | Halbjährlich | Neue Helden-Kräfte & Spielstil |
| **Modding-Support** | Q2 2028 | Custom Cards, Adventures via JSON |
| **Esports-Unterstützung** | Q4 2028 | Turniere, Spectator, Preisgelder |
| **Cross-Platform Sync** | Q1 2029 | Account-Sync über Geräte hinweg |

---

## 7. Quarter-Lookahead (Q4 2026)

| Woche | Fokus | Ziel |
|-------|-------|------|
| **W40-44** | Core Engine Abschluss | MVP ready für Internes Testen |
| **W45-49** | Flet UI Grundgerüst | GameBoard + Deck Builder fertig |
| **W50-52** | Erste KI-Implementierung | Human vs AI Testspielbar |

---

## 8. Quarterly Rhythm (Beispiel: Q1 2027)

```
Monats-Ziele:
- Monat 1: Kampagnen-Framework + 1. Kapitel
- Monat 2: Boss-Mechaniken + Belohnungssystem
- Monat 3: Abenteuer-Modus + Phase 2 Review

Wöchentlich:
- Sprint Planning (Mo)
- Development (Mo-Fr)
- Code Review (Do)
- Demo/Review (Fr)
```

---

## 9. Ressourcen-Planung

| Ressource | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|-----------|---------|---------|---------|---------|
| **Entwickler-Stunden** | 400/h | 500/h | 500/h | 400/h |
| **Design-Zeit** | 80/h | 100/h | 100/h | 80/h |
| **Testing-Zeit** | 60/h | 80/h | 100/h | 80/h |
| **External** | 0 | 0 | 200/h (Netzwerk-Experte) | 150/h (Mobile-OSP) |

---

## 10. Risiko-Management (Roadmap)

| Risiko | Phasen-Betroffen | Wahrscheinlichkeit | Mitigation |
|--------|------------------|-------------------|------------|
| **Scope Creep** | Alle Phasen | Hoch | Strict Phase-Gates, "No" zu Features außerhalb Scope |
| **Flet Performance Mobile** | Phase 4 | Mittel | Early Prototyping Phase 1, Hardware-Tests |
| **PvE Balance** | Phase 2 | Hoch | Beta-Tester, Telemetrie, Parameter-gesteuert |
| **Desync Multiplayer** | Phase 3 | Mittel | Deterministische Engine ab Tag 1 |
| **Scope Reduction** | Phase 1 | Niedrig | MVP-Fokus: Core Loop first, everything else later |

---

*Dokument-Version: 1.0*  
*Status: Planning Phase*  
*Erstellt: 2026-10-03*