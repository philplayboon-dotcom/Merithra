# Merithra – Roadmap

Merithra ist ein PvE-Kartenspiel mit Kämpfen, Karten und dauerhaftem Fortschritt. Diese Roadmap beschreibt geplante Arbeit, nicht den verifizierten Implementierungsstand. Ein Punkt gilt erst als abgeschlossen, wenn Funktion, UI, Persistenz und zugehörige Tests geprüft sind.

## Leitprinzip: der spielbare Kreislauf

Kampf wählen → Deck spielen → Ergebnis und Belohnung erhalten → Fortschritt speichern → Sammlung und Deck anpassen → nächsten Kampf wählen. Zuerst diesen Kreislauf als kleinen Vertical Slice fertigstellen; zusätzliche Ökonomie- und Komfortsysteme folgen danach.

## M0 – Bestehenden Kampfkern absichern (P0)

- [ ] Vorhandene Karten, Effekte, Spielzustände und Spielbrett gegen das Konzept prüfen und ihren tatsächlichen Status dokumentieren.
- [ ] Kampfstart, Zugwechsel, Kartenausspielen, Zielwahl sowie Sieg/Niederlage als vollständigen Ablauf sicherstellen.
- [ ] Reproduzierbare Tests für Regeln, Effekte und Kampfergebnis ergänzen; fehlende oder fehlerhafte Fälle vor der Meta-Progression beheben.

**Abnahme:** Ein PvE-Kampf lässt sich vom Start bis zum Ergebnis ohne manuelle Eingriffe spielen und automatisiert auf zentrale Regeln prüfen.

## M1 – Persistenter PvE-Vertical-Slice (P0)

- [ ] Spielerprofil und versionierten lokalen Spielstand definieren: Kartenbesitz, Decks, Fortschritt und bei Bedarf Guthaben.
- [ ] Spielstand beim Start laden, nach relevanten Änderungen zuverlässig speichern und fehlende/beschädigte Daten behandeln.
- [ ] Kleine PvE-Begegnungsauswahl mit Freischaltung und Abschlussstatus anlegen.
- [ ] Kampfergebnis mit eindeutig definierten Erstabschluss- und Wiederholungsbelohnungen verbinden; doppelte Vergabe verhindern.
- [ ] Mindestens eine neue Karte als Belohnung dauerhaft freischalten und unmittelbar in Sammlung und Deckbau nutzbar machen.

**Abnahme:** Nach einem Sieg bleibt die freigeschaltete Karte auch nach einem Neustart erhalten; Fortschritt und Belohnung werden nicht versehentlich doppelt vergeben.

## M2 – Sammlung und Deckverwaltung (P0)

- [ ] Sammlung als eigenes Fenster bauen: alle verfügbaren Karten, Besitzstatus/Anzahl und Kartendetails anzeigen.
- [ ] Filter und Suche für sinnvolle Eigenschaften wie Kosten, Kartentyp und Seltenheit ergänzen, soweit diese Eigenschaften im Kartensystem existieren.
- [ ] Decks erstellen, bearbeiten, auswählen und speichern.
- [ ] Deckregeln zentral validieren: Größe, zulässige Karten und maximale Kopien entsprechend dem finalen Spieldesign.
- [ ] Leeres Profil mit einem spielbaren Startdeck ausstatten; ungültige Decks vor Kampfstart verständlich erklären.

**Abnahme:** Eine verdiente Karte kann über die Sammlung gefunden, einem gültigen Deck hinzugefügt und im nächsten Kampf gespielt werden.

## M3 – Belohnungen, Währung und Hub (P1)

- [ ] Einfachen Hub mit Zugang zu PvE-Auswahl, Sammlung, Decks und Profil schaffen.
- [ ] Nur falls eine Ausgabe-Mechanik vorgesehen ist: zunächst eine Währung, ihre Quellen, Ausgaben und Obergrenzen definieren.
- [ ] Guthaben im Hub und beim Erhalt/Ausgeben sichtbar machen; Änderungen nachvollziehbar und gegen doppelte Buchung absichern.
- [ ] Eigenes Währungsfenster erst ergänzen, wenn mehrere Währungen, eine Transaktionsübersicht oder komplexere Ökonomie es rechtfertigen.
- [ ] Belohnungsansicht mit klarer Aufschlüsselung für Karten, Währung und gegebenenfalls Gegenstände gestalten.

**Abnahme:** Nach einem Kampf stimmt der angezeigte und gespeicherte Besitz mit der vergebenen Belohnung überein; Ausgaben können nicht zu negativem Guthaben führen.

## M4 – Inventar und weitere Progression (P1, bedingt)

- [ ] Entscheidung dokumentieren, ob Merithra neben Karten überhaupt Gegenstände wie Verbrauchsitems, Schlüssel oder Ausrüstung hat.
- [ ] Nur dann ein getrenntes Inventar mit Gegenstandstyp, Anzahl, Nutzung und Speicherung bauen; Karten bleiben ausschließlich in der Sammlung.
- [ ] Kapitel, Begegnungen, Schwierigkeitsstufen und Freischaltbedingungen ausbauen, sobald der erste Kreislauf stabil ist.
- [ ] Balancing anhand von Kampfdauer, Belohnungsrate und Deckvielfalt prüfen.

**Abnahme:** Falls Gegenstände eingeführt werden, sind Erwerb, Anzeige, Verwendung und Persistenz durchgängig funktionsfähig; andernfalls entfällt das Inventar explizit.

## Später prüfen (P2)

- [ ] Shop, Crafting, Kartenpakete oder mehrere Währungen nur nach definiertem Nutzen und Balancing-Konzept aufnehmen.
- [ ] Erweiterte Komfortfunktionen wie Deckimport/-export, Statistik, Erfolgsübersicht und Barrierefreiheit priorisieren.
- [ ] Zusätzliche PvE-Modi, Bosse und Langzeitprogression auf Basis des getesteten Kernkreislaufs planen.

## Umsetzung und Pflege

- P0 vor P1 vor P2; innerhalb eines Meilensteins Datenmodell und Regeln vor UI-Politur.
- Für jedes Feature ein prüfbares Ergebnis, Testfälle und nötige Migrationen des Spielstands festhalten.
- Checklisten erst nach tatsächlicher Implementierung und Verifikation abhaken; bestehende Konzepte und Regeln in `Konzept.md`, `Design.md` und `ARCHITECTURE.md` bei Entscheidungen abgleichen.
