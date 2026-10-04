# Merithra – Roadmap 0.1

- Zielversion: 0.1.0
- Status: Geplant; Aufgaben nicht als umgesetzt bestätigt
- Erstellt: 2026-10-04
- Analysebasis: main, Commit c6fdfedf04b3b27c24aee9b17e2ba21e5d21a131
- Zweck: Konkreter Release-Meilenstein als Ergänzung zu ROADMAP.md

## 1. Release-Ziel

Merithra startet nicht länger direkt ins GameBoard. Version 0.1 bietet einen Startbildschirm mit provisorischer lokaler Anmeldung, ein Hauptmenü mit den primären Aktionen „Start“ und „Optionen“ und einen vollständig erreichbaren PvE-Testkampf mit Ergebnisanzeige und Rückkehr ins Menü.

```text
Programmstart → Startbildschirm / lokale Anmeldung → Hauptmenü
Hauptmenü → Start → PvE-Testkampf → Ergebnis → Hauptmenü
Hauptmenü → Optionen → Speichern / Abbrechen → Hauptmenü
```

Die langfristige Richtung bleibt Story-PvE mit dauerhaftem Fortschritt, Weltkarte, Städten, Handel und Berufen. Kein Roguelike- oder Permadeath-Modell. Diese Systeme werden nicht zusätzlich zur Voraussetzung für 0.1 gemacht.

## 2. Ausgangsstand

Die folgenden Angaben beziehen sich auf den oben genannten geprüften Commit, nicht auf einen späteren Repository-Stand.

- client/main.py importiert den Einstieg aus client/game_board.py; dort wird unmittelbar ein Kampf aufgebaut.
- core/engine/match.py enthält MatchManager, MatchConfig, Sieg/Niederlage, Retry und Reward-Abfrage.
- GameBoard steuert Aktionen und Zugwechsel noch separat. MatchManager und GameBoard sind deshalb vor dem Release zusammenzuführen.
- PvEAI und die Begegnungen enc_wild_wolf sowie enc_bandit_leader sind vorhanden.
- SaveGameData, create_new_savegame(), SaveManager und ein Migrationsgrundgerüst sind vorhanden.
- Modelle für Inventar, Gold, Städte, Händler, Quests, Berufe und Rezepte sind vorhanden; das ist noch kein vollständiger Story-/Stadt-Flow.
- Tests für Match, Modelle, KI und Speicherung wurden ergänzt. Ein erfolgreicher aktueller Testlauf wurde bei der Repository-Analyse nicht verifiziert.

## 3. Funktionsumfang

### Startbildschirm und Anmeldung

- [ ] Merithra-Schriftzug, provisorischer Hintergrund und Versionsanzeige 0.1.0.
- [ ] Eingabefeld „Spielername“ und Button „Anmelden“.
- [ ] Hinweis „Lokales Testprofil – kein Onlinekonto.“
- [ ] Startbildschirm bei jedem Programmstart; letzten Namen nur vorbelegen.
- [ ] Erstmalige Anmeldung legt ein lokales Profil an; bestehende Profile können wieder ausgewählt werden.
- [ ] Namen nach Trim auf 3–24 Zeichen begrenzen; Buchstaben, Zahlen, Leerzeichen, _ und - zulassen.
- [ ] Interne Profil-ID getrennt vom Anzeigenamen verwenden; Anzeigenamen niemals als Dateipfad benutzen.
- [ ] Keine E-Mail, Passwörter, Tokens oder Serveranbindung für die provisorische Anmeldung.
- [ ] Verständliche Validierungs- und Speicherfehlermeldungen anzeigen.

Die lokale Anmeldung ist eine Profilauswahl, keine Sicherheitsgrenze. Profilverwaltung bleibt hinter einem separaten Service, damit später echte Accounts ergänzt werden können.

### Hauptmenü

- [ ] Zwei primäre Menüpunkte mit den exakten Beschriftungen „Start“ und „Optionen“.
- [ ] Spielername und Version dezent anzeigen.
- [ ] Optional „Profil wechseln“ als sekundäre Aktion, nicht als dritter großer Menüpunkt.
- [ ] „Start“ erzeugt eine frische Partie gegen enc_wild_wolf mit einem festgelegten unterstützten Testdeck.
- [ ] Kein Match beim Öffnen des Menüs oder der Optionen erzeugen.
- [ ] Wiederholte schnelle Start-Klicks dürfen keinen zweiten Match erzeugen.

„Start“ bedeutet in 0.1 „neuen Testkampf starten“, nicht „laufenden Kampf fortsetzen“. Persistenter Kampagnenfortschritt bleibt davon getrennt.

### Optionen

- [ ] Vollbild/Fenstermodus tatsächlich anwenden.
- [ ] Kampflog anzeigen/ausblenden tatsächlich anwenden.
- [ ] „Animationen reduzieren“ nur anbieten, wenn entsprechende Animationen oder Verzögerungen implementiert sind.
- [ ] „Speichern“ übernimmt und persistiert den Einstellungsentwurf.
- [ ] „Abbrechen“ verwirft nicht gespeicherte Änderungen.
- [ ] „Standardwerte“ setzt den Entwurf auf definierte Defaults zurück; Persistenz erst durch Speichern.
- [ ] Einstellungen getrennt vom Kampagnenspielstand speichern und nach Neustart wiederherstellen.

Keine wirkungslosen Lautstärke-, Grafik- oder LLM-Schalter als Platzhalter anbieten.

### Kampf und Rückkehr

- [ ] MatchManager als maßgebliche Kampfsteuerung verwenden.
- [ ] GameBoard delegiert Aktionen und stellt den Zustand dar; keine zweite parallele Kampfsteuerung.
- [ ] Eigene und gegnerische Diener sichtbar und für unterstützte Aktionen auswählbar machen.
- [ ] Sieg/Niederlage als Ergebnisansicht anzeigen und weitere Kampfaktionen sperren.
- [ ] Rückkehr ins Hauptmenü sowie Retry nach Niederlage anbieten.
- [ ] Kampfabbruch bestätigen lassen; keinen dauerhaften Fortschritt zurücksetzen.
- [ ] Laufende KI-Aufgaben und alte Callbacks beim Verlassen beenden oder ungültig machen.
- [ ] Neue Partie ohne alte Hand-, Mana-, Auswahl- oder KI-Zustände starten.

Für 0.1 nur nachweislich unterstützte Karten verwenden. Die geprüfte MatchManager-Implementierung besitzt noch keine vollständige Zauber-/Waffenauflösung. Benötigte Effekte implementieren oder entsprechende Karten aus dem Testdeck entfernen.

## 4. Umsetzung und Reihenfolge

Alle Aufwände sind grobe Schätzungen in konzentrierten Entwicklertagen, keine verbindlichen Termine.

| ID | Meilenstein | Aufgaben | Abnahme | Aufwand |
|---|---|---|---|---|
| M01 | Ausgangsstand absichern | Tests ausführen; Python-/Flet-Version festhalten; pyproject.toml und reproduzierbaren Start ergänzen. | Frischer Checkout lässt sich installieren, starten und testen. | 0,5–1 Tag |
| M02 | App-Einstieg entkoppeln | Page-Setup nach app.py; AppState und zentrale Navigation; regulären Direktstart des Boards ablösen. | Programmstart zeigt nur den Startbildschirm; kein aktiver Match. | 0,5–1 Tag |
| M03 | Lokales Profil | Profilmodell, Service, Persistenz, Namensvalidierung und Startansicht. | Gültige Anmeldung öffnet Menü; ungültige Eingaben bleiben auf Startansicht; Profil wieder auswählbar. | 1–1,5 Tage |
| M04 | Hauptmenü | Start, Optionen, Profil-/Versionsanzeige; optional Profilwechsel. | Navigation ohne unbeabsichtigten Kampfstart. | 0,5 Tag |
| M05 | Optionen | Einstellungsmodell, Entwurf, Speichern/Abbrechen, Persistenz und reale Anwendung. | Einstellungen wirken und bleiben nach Neustart erhalten. | 0,5–1 Tag |
| M06 | Kampf integrieren | GameBoard an MatchManager anbinden; unterstütztes Testdeck; Ergebnis, Retry, Abbruch und Cleanup. | Start → Kampf → Ergebnis → Menü; erneuter Start liefert frische Partie. | 1,5–3 Tage |
| M07 | Release absichern | Regressionstests, manueller Smoke-Test, Dokumentation, Changelog und Version. | Release-Checkliste vollständig erfüllt. | 1–2 Tage |

Planungsrahmen: ungefähr 5–10 konzentrierte Entwicklertage. Hauptunsicherheit ist die Zusammenführung von GameBoard und MatchManager. Umsetzung in der Reihenfolge M01 bis M07; keine zusätzlichen Story-/Wirtschaftsfeatures vor dem Release einschieben.

## 5. Technische Struktur

Die folgende Struktur ist ein Vorschlag; neue Dateien sind noch nicht implementiert.

```text
client/
  main.py
  app.py
  navigation.py
  state.py
  game_board.py
  theme.py
  screens/
    start_screen.py
    main_menu_screen.py
    options_screen.py
    result_screen.py
core/
  profiles/
    models.py
    service.py
  settings.py
  engine/match.py
  storage/
    manager.py
    profile_store.py
    settings_store.py
tests/
  test_navigation.py
  test_profiles.py
  test_settings.py
  test_app_flow.py
```

- main.py: einziger regulärer Programmeinstieg.
- AppController: Bildschirmwechsel, Start/Ende eines Matches und Rückkehrlogik.
- AppState: aktives Profil, Settings und höchstens ein aktiver Match; pro App-Sitzung instanziieren.
- ProfileService: lokale Profilidentität, keine Kampfregeln.
- MatchManager: maßgebliche Kampfsteuerung.
- GameBoard: Eingaben weiterreichen und Spielzustand rendern.
- SaveManager: vorhandene Persistenz wiederverwenden. Profil und Spielstand über interne IDs zuordnen; keine gemeinsamen slot_1-Spielstände für verschiedene Profile.

Navigation ohne Profil zu Menü/Kampf blockieren. Speicherfehler nicht als Neuanlage interpretieren: SaveManager.load() liefert im geprüften Stand sowohl bei fehlender Datei als auch bei Ladefehlern None. Diese Fälle unterscheiden und beschädigte Spielstände niemals stillschweigend überschreiben.

## 6. Tests und Release-Abnahme

### Automatisierte Tests

- [ ] Startzustand: Startbildschirm sichtbar, Profil nicht aktiv, kein Match erzeugt.
- [ ] Namen: leer, nur Leerzeichen, zu kurz/lang, gültige Sonderfälle und äußere Leerzeichen.
- [ ] Profil: anlegen, wieder auswählen, getrennte Spielstände und Fehlerbehandlung.
- [ ] Navigation: ohne Profil blockiert; Optionen erzeugen keinen Match.
- [ ] Settings: Defaults, Speichern, Abbrechen, Neustart und beschädigte Settings-Datei.
- [ ] Start-Doppelklick: höchstens ein aktiver Match.
- [ ] Match: Sieg/Niederlage, Aktionssperre, Retry, Rückkehr und frische zweite Partie.
- [ ] Cleanup: keine KI-Aktion aktualisiert nach Verlassen die alte Ansicht.
- [ ] Bestehende Core- und GameBoard-Tests bleiben erfolgreich.

### Manueller Smoke-Test

1. Anwendung aus frischer Installation starten.
2. Ungültigen Namen eingeben und Fehlermeldung prüfen.
3. Mit gültigem lokalen Profil anmelden.
4. Optionen ändern, abbrechen und unveränderte Werte prüfen.
5. Optionen ändern, speichern, Anwendung neu starten und Persistenz prüfen.
6. Profil erneut auswählen und Testkampf starten.
7. Kampf bis Sieg oder Niederlage spielen und Ergebnisansicht prüfen.
8. Ins Menü zurückkehren und zweite frische Partie starten.
9. Kampf während eines KI-Zuges verlassen und ausbleibende alte Updates prüfen.
10. Kontrollieren, dass Niederlage/Abbruch keinen dauerhaften Fortschritt löscht.

### Definition of Done

- [ ] Startbildschirm erscheint bei jedem Programmstart.
- [ ] Anmeldung und Hauptmenü funktionieren vollständig offline.
- [ ] Hauptmenü besitzt die primären Aktionen Start und Optionen.
- [ ] Einstellungen wirken; Speichern und Abbrechen unterscheiden sich.
- [ ] Start → PvE-Kampf → Ergebnis → Menü ist vollständig spielbar.
- [ ] Keine veralteten Match-/KI-Zustände nach Rückkehr oder Neustart.
- [ ] Keine stillschweigende Überschreibung beschädigter Spielstände.
- [ ] Alle automatisierten Tests bestehen; Smoke-Test dokumentiert.
- [ ] SETUP.md, ARCHITECTURE.md und TESTING.md mit dem implementierten Ablauf abgeglichen.
- [ ] Version 0.1.0, Changelog und Release-Hinweise mit bekannten Einschränkungen gepflegt.
- [ ] Release erst danach als v0.1.0 markieren.

## 7. Außerhalb von 0.1

- Vollständige Weltkarte und Städteansichten.
- Händler-, Inventar-, Crafting- und Berufsoberflächen.
- Deckbuilder und Sammlungsoberfläche.
- Vollständiger Story-Abschnitt mit Reise-/Questintegration.
- Online-Accounts, Cloud-Sync und Multiplayer.
- Verpflichtende LLM-Integration.
- Fortsetzen laufender Kämpfe nach Programmneustart.

Diese Features bleiben im langfristigen Backlog und sind keine Release-Blocker für 0.1.

## 8. Empfohlene Arbeitspakete

1. refactor: introduce application shell and navigation
2. feat: add start screen and local profile login
3. feat: add main menu and persistent options
4. refactor: connect game board to match manager
5. test: cover v0.1 application flow and prepare release

Die allgemeine ROADMAP.md bleibt bestehen. Dieses Dokument konkretisiert ausschließlich den Einstieg und den begrenzten spielbaren Umfang der Version 0.1.
