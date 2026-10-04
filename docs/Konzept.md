# Merithra – Konzept

## Vision

Merithra ist ein storyorientiertes PvE-Kartenspiel mit strategischem Deckbau, einer bereisbaren Welt und dauerhaftem Spielfortschritt. Eine zusammenhängende Kampagne führt durch mehrere Städte und Regionen. Städte dienen als Anlaufpunkte für Warenhandel, Quests, Berufe, Crafting und weitere Aktivitäten.

Der zentrale Spielkreislauf lautet: **Welt erkunden → Story und Aufgaben verfolgen → Kartenkämpfe bestreiten → Belohnungen und Materialien erhalten → Städte besuchen, handeln und herstellen → Sammlung und Deck verbessern → neue Regionen und Kapitel erschließen.**

## Kernpfeiler

### 1. PvE als Differenzierungsmerkmal

- **Fokus auf Story & Kampagne**: Ein zusammenhängendes Einzelspieler-Erlebnis gegen thematisch gestaltete KI-Gegner und Bosse.
- **Kein kompetitiver PvP-Druck**: Das Spiel ist auf strategische Herausforderungen im PvE ausgelegt.
- **Zielgruppe**: Spieler, die strategisches Kartenspiel mit Rollenspiel- und Weltelementen schätzen.

### 2. Strategischer Deckbau & Sammlung

- **Tiefes Synergiesystem**: Spieler experimentieren mit Kartenkombinationen, um optimale Decks für unterschiedliche PvE-Herausforderungen zusammenzustellen.
- **Dauerhafte Sammlung**: Freigeschaltete Karten bleiben dauerhaft im Besitz des Spielers.
- **PvE-fokussierte Balance**: Karteneffekte und Mechaniken sind auf abwechslungsreiche PvE-Begegnungen abgestimmt.

### 3. Persistente Welt & Fortschritt

- **Dauerhafter Spielstand**: Niederlagen setzen weder die Kampagne noch Sammlung, Berufe oder freigeschaltete Orte zurück. Kämpfe können ohne Fortschrittsverlust erneut versucht werden.
- **Bereisbare Weltkarte**: Regionen und Städte werden über Story- und Quest-Fortschritt freigeschaltet.
- **Städte & Wirtschaft**: Händler, Warenhandel, Quests, NPCs und Werkstätten.
- **Berufe & Crafting**: Sammeln von Rohstoffen und Herstellen von Gegenständen, Handelswaren und Karten.

## Gameplay-Loop

1. **Reisen & Erkunden**: Auf der Weltkarte Orte ansteuern, Quests annehmen und Händler besuchen.
2. **Kartenkämpfe bestreiten**: Strategische Karteneinsätze gegen PvE-Gegner und Bosse.
3. **Belohnungen sichern**: Gold, Materialien, neue Karten und Questfortschritt erhalten.
4. **Handeln & Herstellen**: In Städten Berufe ausüben, Gegenstände craften und gewinnbringend handeln.
5. **Deck & Charakter optimieren**: Sammlung verwalten, Decks verfeinern und für neue Kapitel wappnen.

## Technische Umsetzung

- **Plattform**: Desktop / Cross-Platform
- **Programmiersprache**: Python 3.11+ (typisiert)
- **UI-Framework**: Flet (Flutter-basiert)
- **Persistenz**: Versioniertes Speichersystem (JSON / SQLite) mit sicherer Migration
- **Optionale KI**: Lokale LLM-Integration via Ollama (Qwen3 für Strategie, Llama 3.2 für Companion-Chat)

## Roadmap & Meilensteine

Die detaillierten Entwicklungsphasen (Phase 1 bis Phase 6) und Abnahmekriterien sind in [`docs/ROADMAP.md`](file:///C:/Users/jamie/Documents/Repos/Merithra/docs/ROADMAP.md) festgelegt.
