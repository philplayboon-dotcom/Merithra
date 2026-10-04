# Merithra – Roadmap

## Vision

Merithra ist ein storyorientiertes PvE-Kartenspiel mit strategischem Deckbau, einer bereisbaren Welt und dauerhaftem Spielfortschritt. Eine zusammenhängende Kampagne führt durch mehrere Städte und Regionen. Städte dienen als Anlaufpunkte für Warenhandel, Quests, Berufe, Crafting und weitere Aktivitäten.

Der zentrale Spielkreislauf lautet: Welt erkunden → Story und Aufgaben verfolgen → Kartenkämpfe bestreiten → Belohnungen und Materialien erhalten → Städte besuchen, handeln und herstellen → Sammlung und Deck verbessern → neue Regionen und Kapitel erschließen.

Die Kampagne verwendet einen persistenten Spielstand. Niederlagen setzen weder die Kampagne noch Sammlung, Berufe oder freigeschaltete Orte zurück. Kämpfe können erneut versucht werden. Es gibt keine Run-Struktur, keinen Permadeath und keinen Neustartzyklus als Progressionsmodell.

## Planungsstatus

Alle nachfolgenden Checkboxen beschreiben zu prüfende beziehungsweise geplante Arbeitspakete, nicht einen verifizierten Implementierungsstand. Die Roadmap priorisiert Abhängigkeiten und spielbare Meilensteine statt fester Termine.

## Phase 1 – Technische Basis und Kartenkampf

Ziel: Eine zuverlässige Grundlage für Kartenkämpfe und den späteren Kampagnenspielstand schaffen.

- [ ] Kartenmodell, Ressourcen, Zugablauf, Ziele und Effekte konsistent definieren und testen.
- [ ] Sieg, Niederlage und erneuten Kampfversuch sauber abbilden.
- [ ] PvE-Gegner mit regelkonformer KI und unterschiedlichen Deckstrategien implementieren.
- [ ] Kampfoberfläche mit verständlichen Kartenwerten, Zuständen und strukturiertem Kampflog ausarbeiten.
- [ ] Karten aus wiederverwendbaren Grafikbausteinen aufbauen; Werte und Zustand als getrennte Overlays darstellen.
- [ ] Datenmodelle für Karten, Gegenstände, Materialien, Rezepte, Berufe, Quests, Städte und Regionen vorbereiten.
- [ ] Versioniertes Speichersystem mit Laden, Migrationen und sicherem Speichern einrichten.
- [ ] Automatisierte Tests für Kampfregeln und Speicherung etablieren.

Abnahmekriterium: Ein vollständiger PvE-Kampf ist spielbar, kann nach einer Niederlage erneut gestartet werden und beschädigt den gespeicherten Fortschritt nicht.

## Phase 2 – Persistenter Fortschritt und Deckbau

Ziel: Kartenkämpfe mit einer dauerhaft nutzbaren Sammlung und Wirtschaftsbasis verbinden.

- [ ] Kartensammlung mit Suche, Filtern und Detailansichten erstellen.
- [ ] Deckeditor mit Speichern, Laden und Validierung der Deckregeln implementieren.
- [ ] Inventar für Waren, Materialien und sonstige Gegenstände mit Mengen und Detailansichten einführen.
- [ ] Währungsmodell und zentrale Anzeige für Guthaben und Transaktionen ergänzen.
- [ ] Belohnungen aus Kämpfen und Quests zuverlässig in Sammlung, Inventar und Guthaben übertragen.
- [ ] Mehrfachvergabe derselben einmaligen Belohnung verhindern; Wiederholungsbelohnungen ausdrücklich definieren.
- [ ] Sammlung, Decks, Inventar, Guthaben und Freischaltungen gemeinsam speichern.
- [ ] Hauptnavigation für Kampf, Sammlung, Deckbau, Inventar, Questlog und Weltkarte vorbereiten.

Abnahmekriterium: Eine erhaltene Karte oder Ware bleibt nach einem Neustart verfügbar; Karten lassen sich einem gültigen Deck hinzufügen.

## Phase 3 – Story-Modus und Weltkarte

Ziel: Eine zusammenhängende Kampagne mit dauerhaft zugänglichen Orten statt isolierter Kämpfe anbieten.

- [ ] Story-Struktur mit Kapiteln, Hauptquests, Nebenquests und Kapitelbossen entwerfen.
- [ ] Questzustände, Voraussetzungen, Ziele, Belohnungen und Dialogfortschritt implementieren.
- [ ] Questlog mit aktuellen Aufgaben und nachvollziehbaren Zielorten erstellen.
- [ ] Weltkarte mit mehreren Regionen, Städten, Routen und Begegnungsorten entwickeln.
- [ ] Aktuellen Standort, erreichbare Ziele und gesperrte Gebiete auf der Karte anzeigen.
- [ ] Reisen zwischen freigeschalteten Orten und Rückkehr in bereits besuchte Städte ermöglichen.
- [ ] Neue Orte über Story-Fortschritt und klar definierte Voraussetzungen freischalten.
- [ ] Story-Kämpfe und Bossbegegnungen mit der Karte und dem Questfortschritt verbinden.
- [ ] Regeln für Niederlagen und wiederholbare Begegnungen festlegen, ohne Kampagnenfortschritt zurückzusetzen.
- [ ] Standort, Questzustände, Kapitel und Kartenfreischaltungen persistent speichern.

Abnahmekriterium: Der Spieler reist auf der Weltkarte zwischen zwei Städten, erfüllt eine Hauptquest und schaltet einen weiteren Ort frei. Nach dem Laden bleibt dieser Fortschritt erhalten.

## Phase 4 – Städte, Warenhandel und Aktivitäten

Ziel: Mehrere unterscheidbare Städte als spielerisch relevante Anlaufpunkte etablieren.

- [ ] Ein erweiterbares Stadtmodell mit Händlern, NPCs, Dienstleistungen und Aktivitäten entwickeln.
- [ ] Mehrere Städte mit eigenem Profil, Warenangeboten, Questkontakten und verfügbaren Berufen gestalten.
- [ ] Stadtansicht mit direktem Zugang zu Markt, Werkstätten, Questgebern und weiteren Aktivitäten erstellen.
- [ ] Händleroberfläche für Warenkauf und -verkauf mit Mengenwahl, Preisvorschau und Transaktionsbestätigung implementieren.
- [ ] Warenbestände und Preisregeln definieren; regionale Unterschiede für Handel zwischen Städten vorsehen.
- [ ] Käufe und Verkäufe atomar ausführen und ungültige Mengen, fehlendes Guthaben sowie Duplizierung verhindern.
- [ ] Weitere Stadtaktivitäten zunächst als kleine Auswahl umsetzen, etwa lokale Aufträge, Trainingskämpfe oder Tavernenbegegnungen.
- [ ] Stadtaktivitäten mit Story, Belohnungen, Handelswaren und späteren Handwerksmaterialien verknüpfen.
- [ ] Händlerangebote, relevante NPC-Zustände und abgeschlossene Aktivitäten speichern.

Abnahmekriterium: In mindestens zwei Städten können Waren gekauft und verkauft sowie unterschiedliche lokale Aktivitäten genutzt werden. Waren und Guthaben bleiben nach dem Laden konsistent.

## Phase 5 – Berufssystem und Crafting

Ziel: Berufe als dauerhaften Teil der Charakterentwicklung und Stadtwirtschaft integrieren.

- [ ] Berufssystem mit Freischaltung, Erfahrung, Stufen und Rezeptzugang definieren.
- [ ] Für den ersten spielbaren Umfang mindestens einen vollständig nutzbaren Beruf auswählen; weitere Berufe datengetrieben ergänzbar halten.
- [ ] Mögliche Berufe wie Alchemie, Schmiedekunst oder Kartenherstellung auf ihren Nutzen für das Kartenspiel prüfen.
- [ ] Materialien über Quests, Kämpfe, Händler und passende Welt- oder Stadtaktivitäten zugänglich machen.
- [ ] Rezeptmodell mit Zutaten, Mengen, Berufsvoraussetzungen, Werkstattanforderungen und Ergebnis implementieren.
- [ ] Crafting-Oberfläche mit Rezeptfiltern, Zutatenübersicht, Fehlmengen und Herstellungsmenge erstellen.
- [ ] Zutatenverbrauch, Ergebnisvergabe und Berufserfahrung als eine konsistente Transaktion ausführen.
- [ ] Werkstätten und Berufslehrer in geeigneten Städten integrieren.
- [ ] Herstellung nützlicher Handelswaren und spielrelevanter Gegenstände planen; konkrete Kartenvorteile vor Einführung balancieren.
- [ ] Berufserfahrung, freigeschaltete Rezepte und hergestellte Gegenstände speichern.
- [ ] Materialbedarf, Herstellungsnutzen und Verkaufserlöse gemeinsam mit der Handelswirtschaft testen.

Abnahmekriterium: Der Spieler erwirbt Materialien, stellt in einer Stadt ein Rezept her, erhält das Ergebnis und Berufserfahrung und kann das Produkt verwenden oder verkaufen. Alles bleibt nach dem Laden erhalten.

## Phase 6 – Inhalte, Balance und Veröffentlichung

Ziel: Den vollständigen Kampagnenkreislauf ausbauen und veröffentlichungsreif machen.

- [ ] Weitere Story-Kapitel, Städte, Regionen, Gegner und Bosskämpfe ergänzen.
- [ ] Zusätzliche Berufe, Rezepte, Handelswaren und Stadtaktivitäten ausbauen.
- [ ] Kartenbalance, Kampagnenschwierigkeit und Belohnungen gemeinsam abstimmen.
- [ ] Wirtschaft auf unbegrenzte Gewinnschleifen, übermäßigen Grind und nutzlose Waren prüfen.
- [ ] Tutorial für Kampf, Deckbau, Weltkarte, Handel und Crafting erstellen.
- [ ] UI, Tooltips, Fehlermeldungen, Lesbarkeit und Bedienkomfort vereinheitlichen.
- [ ] Audio, Animationen und Performance optimieren.
- [ ] Integrations- und Regressionstests für den gesamten Spielkreislauf ergänzen.
- [ ] Savegame-Migrationen, Unterbrechungen beim Speichern und fehlerhafte Transaktionen testen.
- [ ] Plattformumfang, Veröffentlichungspaket und Release-Checkliste festlegen.

Abnahmekriterium: Die geplante Story ist durchspielbar; Reisen, Stadtaktivitäten, Handel, Crafting, Sammlung und Deckbau funktionieren gemeinsam ohne Fortschrittsverlust.

## Meilensteine

| Meilenstein | Spielbarer Umfang |
| --- | --- |
| Kampfprototyp | Vollständiger PvE-Kampf mit Wiederholungsoption und verlässlichen Regeln. |
| Persistenz-Prototyp | Sammlung, Deckbau, Inventar, Guthaben und Speichern/Laden bilden einen dauerhaften Fortschrittskreislauf. |
| Story-Vertical-Slice | Ein Story-Abschnitt, zwei Städte, eine verbindende Weltkartenroute, Warenhandel, mindestens eine zusätzliche Stadtaktivität und ein Beruf mit Crafting. |
| Alpha | Die zentralen Kampagnen-, Weltkarten-, Stadt-, Handels- und Berufssysteme sind integriert; Inhalte werden ausgebaut. |
| Beta | Der geplante Story-Umfang ist spielbar; Schwerpunkt auf Balance, Wirtschaft, UI und Savegame-Stabilität. |
| Release | Getestete Kampagne mit mehreren Städten, Weltkarte, Warenhandel und Berufssystem samt Crafting. |

## Offene Designentscheidungen

- [ ] Anzahl und Identität der Städte sowie Umfang der Kampagne festlegen.
- [ ] Erste Berufe, erlernbare Berufszahl und mögliche Spezialisierungen bestimmen.
- [ ] Rolle von hergestellten Gegenständen, Verbrauchsgütern und gegebenenfalls Karten festlegen.
- [ ] Preisbildung, Händlerbestände, Reisedauer und etwaige Reisekosten definieren.
- [ ] Art und Umfang der Stadtaktivitäten auswählen.
- [ ] Regeln für wiederholbare Kämpfe, Belohnungen und Niederlagenkosten konkretisieren.
- [ ] Zielplattformen und Umfang der ersten Veröffentlichung bestimmen.

## Dokumentationsabgleich

Diese Roadmap definiert die neue Entwicklungsrichtung. Konzept.md, Design.md und ARCHITECTURE.md müssen anschließend auf Übereinstimmung mit Story-Kampagne, Städten, Weltkarte, Handel und Berufen geprüft werden. Bestehende Beschreibungen eines Run-basierten Progressionsmodells sind dort in einem separaten Dokumentationsschritt zu ersetzen. Diese Änderung betrifft ausschließlich docs/ROADMAP.md.
