# Merithra – Roadmap zur lokalen LLM-Integration

- Datei: Roadmap-to-LLM.md
- Erstellt: 2026-10-04
- Status: Implementierungsplan, keine Bestätigung bereits implementierter LLM-Funktionen
- Voraussetzung: Abgeschlossene Version 0.1.0 gemäß Roadmap_0.1.md
- Vorgeschlagener Folgemeilenstein: 0.2.0 „Local LLM Preview“
- Grundprinzip: Lokale LLM optional; Engine und regelbasierte PvE-KI bleiben funktionsfähig.

## 1. Ziel und Planungsbasis

Merithra erhält eine lokale Ollama-Anbindung für zwei getrennte Rollen:

1. Strategie: Qwen3 4B als Ausgangskandidat für Zugberatung und später optionale Gegnerentscheidungen.
2. Companion: Llama 3.2 3B als Ausgangskandidat für einen deutschsprachigen Kartenmeister namens Rook, der Spielzustände kommentiert und dokumentierte Regeln erklärt.

Diese Modelle folgen der bisherigen Projektplanung. Ihre tatsächliche Eignung, unterstützten Request-Parameter, Latenz und Ressourcenbedarf werden auf der Zielhardware geprüft. Modell-Tags allein garantieren keine bestimmte Quantisierung oder reproduzierbaren Antworten.

Die LLM verändert niemals unmittelbar Mana, Lebenspunkte, Karten, Inventar, Gold, Quests oder Spielstände. Sie liefert Text oder wählt eine von der Engine bereitgestellte Aktion. Die Engine validiert und führt diese Aktion aus.

Die vom Nutzer als erfüllt angegebenen 0.1-Änderungen bilden die Planungsbasis. Ihre Umsetzung wurde für dieses Dokument nicht erneut im Repository verifiziert. M-LLM-00 prüft deshalb die tatsächlichen Schnittstellen, bevor neue Module entstehen.

### Übernommene 0.1-Funktionen

- Startbildschirm mit lokaler Profilanmeldung.
- Hauptmenü mit „Start“ und „Optionen“.
- Zentraler AppController mit AppState und geschützter Navigation.
- Persistente Einstellungen mit Speichern/Abbrechen.
- MatchManager als maßgebliche Kampfsteuerung.
- GameBoard als Darstellung und Eingabeschicht.
- Ergebnisansicht, Retry, Rückkehr ins Menü und Cleanup laufender KI-Aufgaben.
- Getrennte lokale Profile und Kampagnenspielstände.

Keinen zweiten AppController, keine zweite Profilverwaltung und keinen parallelen Kampflifecycle bauen. Vorhandene Module erweitern; die hier vorgeschlagenen Dateinamen an die tatsächlich umgesetzte Struktur anpassen.

## 2. Release-Umfang

### Verbindlich für Local LLM Preview

- [ ] Ollama asynchron erreichen und lokal installierte Modelle erkennen.
- [ ] LLM-Einstellungen in die vorhandenen Optionen integrieren.
- [ ] Companion-Chat im GameBoard mit deutscher Sprache und begrenzter Historie anbieten.
- [ ] „Zug vorschlagen“ liefert einen Vorschlag aus den aktuell legalen Aktionen.
- [ ] Optionaler Button „Vorschlag ausführen“ validiert den Vorschlag erneut.
- [ ] Fehler, fehlende Modelle und langsame Antworten lassen den normalen Spielablauf weiterlaufen.
- [ ] Profilwechsel, Matchende, Retry und Navigation verhindern verspätete UI-Updates.
- [ ] Automatisierte Tests ohne Ollama sowie gesonderte echte Ollama-Smoke-Tests.

### Optional nach stabiler Beratung

- [ ] Gegnerzüge durch Strategie-LLM auswählen lassen.
- [ ] Pro Gegnerzug ein begrenztes Gesamtzeitbudget mit heuristischem Fallback einhalten.
- [ ] Einfaches Ressourcenprofil für ein gemeinsames Modell beziehungsweise getrennte Modelle anbieten.

Wenn der optionale Gegnermodus noch nicht stabil ist, die Preview mit Companion und Zugberatung ausliefern. Dieser Modus ist kein Grund, die vorherigen Funktionen zurückzuhalten.

### Nicht Bestandteil dieses Meilensteins

- Cloud-Provider, API-Schlüssel, Onlinekonten oder Multiplayer.
- Autonome Agenten mit Dateisystem-, Shell-, Browser- oder Schreibzugriff.
- Automatische Quest-, Wirtschaft-, Karten- oder Savegame-Änderungen durch Modelltext.
- Vektordatenbank, umfangreiches RAG, Fine-Tuning, Sprachsteuerung oder Bilderkennung.
- Freies Erfinden neuer verbindlicher Spielregeln.
- Zwangsinstallation, automatischer Modell-Download oder automatisch gestarteter Ollama-Dienst.

## 3. Architektur und Integrationspunkte

```text
Vorhandene App / Optionen / GameBoard
             ↓
         LLMService
         ├── CompanionService → sichtbarer Zustand + geprüfte Regeln → Text
         └── StrategyService → sichtbarer Zustand + legale Aktionen → action_id
             ↓
         OllamaProvider (asynchron)
             ↓
         Ollama auf 127.0.0.1:11434

Strategievorschlag → Schema-Prüfung → Kontextprüfung → Engine-Validierung
                                                     ↓
                                                Engine-Ausführung

Fehler / Timeout → Beratung nicht verfügbar oder heuristische PvE-KI
```

### Vorgeschlagene Module

```text
core/
  llm/
    contracts.py            # Requests, Responses, Status und Provider-Interface
    ollama_provider.py      # Asynchroner Transport, Modellabfrage, Timeouts
    service.py              # Queue, Lifecycle, Ressourcen- und Fehlersteuerung
    snapshots.py            # Sichtbarkeitsgefilterte Zustandsprojektionen
    strategy.py             # Entscheidung aus legalen Aktionen
    companion.py            # Deutschsprachiger Chat, Regeln, Historienlimit
    prompts.py              # Versionierte Prompt-Vorlagen
    metrics.py              # Lokale technische Messwerte ohne Chattext
  engine/
    actions.py              # Gemeinsame Action-Contracts, falls noch nicht vorhanden
    match.py                # Vorhandenen MatchManager erweitern
client/
  components/
    companion_panel.py
    llm_status.py
  screens/
    options_screen.py       # Vorhandene Optionen erweitern
  state.py                  # Settings-/Session-Felder ergänzen
  app.py                    # Lifecycle-Hooks ergänzen
resources/
  rules_de.md               # Geprüfte Regeln des tatsächlich unterstützten Kartensatzes
tests/
  llm/
    test_provider.py
    test_snapshots.py
    test_strategy.py
    test_companion.py
    test_lifecycle.py
    test_llm_settings.py
    test_ollama_integration.py
```

Ordner sind ein Vorschlag und keine Aussage über den neuen tatsächlichen Dateibestand.

### Verantwortlichkeiten

- MatchManager liefert Snapshots und legale Aktionen und validiert die Ausführung.
- LLMService hält einen asynchronen Transport und begrenzt parallele Requests.
- OllamaProvider kennt HTTP/Ollama, aber keine Flet-Control-Referenzen und keine Spielregeln.
- StrategyService darf nur eine bereitgestellte action_id zurückgeben.
- CompanionService darf nur Text liefern und keine Engine-Methoden aufrufen.
- AppController meldet Profilwechsel, Matchende, Retry und Appende an den LLMService.
- GameBoard zeigt Ladezustand, Vorschläge, Fehlerhinweise und Companion-Text; Netzwerkzugriff niemals synchron im UI-Handler.

Als initialen Transport einen asynchronen HTTP-Client, beispielsweise httpx.AsyncClient, verwenden und als Projektabhängigkeit festhalten. Nicht gleichzeitig mehrere SDK-/HTTP-Abstraktionen für denselben Zweck einführen.

## 4. Optionen und Startablauf

Die lokale Profilanmeldung bleibt unverändert. LLM-Verfügbarkeit darf Anmeldung, Menü und Start eines normalen PvE-Kampfes nicht blockieren.

### Erweiterung der vorhandenen Optionen

| Einstellung | Default | Verhalten |
|---|---|---|
| Lokale LLM verwenden | Aus | Aktiviert optionale Dienste, keine Voraussetzung zum Spielen. |
| Companion aktivieren | Aus | Chatpanel nach erfolgreichem Modellcheck verfügbar. |
| Zugberatung aktivieren | Aus | Button „Zug vorschlagen“ im eigenen Zug verfügbar. |
| LLM-Gegner verwenden | Aus | Erst nach Abnahme des optionalen Gegnermodus anbieten. |
| Strategiemodell | qwen3:4b | Auswahl aus lokal erkannten Modellen. |
| Companion-Modell | llama3.2:3b | Auswahl aus lokal erkannten Modellen. |
| Ressourcenprofil | Ein Request gleichzeitig | Keine gleichzeitige Strategie-/Companion-Generierung. |
| Verbindung prüfen | Aktion | Prüft Ollama und Modellbestand asynchron. |

„Speichern“ übernimmt die Einstellungen; „Abbrechen“ darf weder dauerhafte Settings ändern noch einen Modellwechsel aktivieren. Ein Verbindungstest darf lediglich den eingegebenen Konfigurationsentwurf prüfen.

Endpunkt in der Preview auf Loopback festlegen: http://127.0.0.1:11434. Falls später ein Portfeld hinzukommt, Host weiterhin auf Loopback beschränken, Proxy-Umgebungsvariablen für diesen Client nicht übernehmen und keine Redirects zu externen Hosts verfolgen. Keine Cloud-Modell-Tags auswählen oder ungefragt nachladen; nur bereits lokal verfügbare, für Offlinebetrieb getestete Modelle freigeben.

### Initialer Ablauf

1. App startet und lädt die vorhandenen Einstellungen; keine blockierende Modellgenerierung.
2. Nutzer meldet sich am lokalen Profil an.
3. Bei aktivierter LLM erfolgt ein zeitlich begrenzter Hintergrundcheck.
4. Hauptmenü bleibt nutzbar, auch wenn der Check fehlschlägt.
5. GameBoard zeigt „Bereit“, „Ollama nicht erreichbar“, „Modell fehlt“ oder „Antwort wird erstellt“.
6. Ohne LLM bleibt „Start“ ein normaler Kampf gegen die vorhandene Heuristik-KI.

### Einrichtungsanleitung

Ollama vorab separat installieren und starten. Downloads sind ein bewusster Einrichtungsschritt; der spätere Spielbetrieb benötigt bei lokal vorhandenen Modellen kein Internet.

```bash
ollama pull qwen3:4b
ollama pull llama3.2:3b
ollama list
```

Für den ersten ressourcenschonenden Test kann ein einzelnes lokal getestetes Modell beide Rollen übernehmen. Das ist eine Option, keine Qualitätsgarantie. Keine pauschale RAM-/VRAM-Mindestanforderung veröffentlichen, bevor eigene Messungen vorliegen.

## 5. Ollama-Provider und Fehlerverhalten

### API-Vertrag

- GET /api/tags: Installierte Modelle und Metadaten abfragen.
- POST /api/chat: Chat-/Strategieantwort erzeugen.
- Strategie anfangs mit stream=false; vollständige strukturierte Antwort validieren.
- Companion zunächst ebenfalls mit stream=false; Streaming erst nach stabiler Lifecycle-Integration ergänzen.
- format kann ein JSON-Schema sein; trotzdem jede Antwort lokal validieren.
- keep_alive ist konfigurierbar; Speicherbedarf und Wechselkosten auf Zielhardware messen.
- think nur verwenden, wenn Modell und lokale Ollama-Version es unterstützen; als Startkonfiguration für Strategie bei unterstützten Modellen deaktivieren.

API-Grundlage: [Chat-Endpunkt](https://docs.ollama.com/api/chat), [lokale Modellliste](https://docs.ollama.com/api/tags) und [Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs).

### Vorgeschlagene Startbudgets

Diese Werte sind Konfigurationsvorschläge und Abnahmestartpunkte, keine gemessenen Leistungsversprechen.

| Request | Startbudget | Verhalten bei Überschreitung |
|---|---:|---|
| Verbindungs-/Modellcheck | 3 Sekunden insgesamt | Status setzen, normal weiterspielen. |
| Zugberatung | 8 Sekunden insgesamt | Kein Vorschlag; erneute Anfrage nur auf Nutzeraktion. |
| Companion | 20 Sekunden insgesamt | Kurzer Fehlerhinweis; Historie bleibt konsistent. |
| Optionaler LLM-Gegnerzug | 10 Sekunden für den ganzen Zug | Restliche Entscheidungen durch Heuristik-KI. |

Ein echter Gesamttimeout umfasst Queue-Wartezeit, Modellladen, Generierung und gegebenenfalls Reparaturanfrage. Einzelne HTTP-Lese-Timeouts ersetzen diese Deadline nicht. Den asynchronen Aufruf zusätzlich mit einer Gesamtabbruchgrenze versehen.

- Maximal ein aktiver Generierungsrequest in der ersten Integration.
- Maximal eine wartende manuelle Anfrage; weitere Klicks deaktivieren oder eindeutig ablehnen.
- Strategie vor neuem Companion-Request priorisieren; keine bereits laufende Generierung ohne definierten Abbruchmechanismus verdrängen.
- Optional genau eine Schema-Reparaturanfrage nur innerhalb des verbleibenden Gesamtbudgets.
- Bei Transportfehlern/Timeout kein automatischer Retry-Sturm.
- Nach drei aufeinanderfolgenden Transportfehlern 30 Sekunden automatische Anfragen pausieren; manueller Verbindungstest bleibt möglich.
- Request-Abbruch ist best effort: Lokale Antworten zuverlässig verwerfen, selbst wenn Ollama intern noch weiterrechnet.
- Modellwechsel erst für neue Requests aktivieren; laufende Antwort durch Konfigurationsgeneration invalidieren.

## 6. Zentrale Aktionen und sichere Snapshots

Vor der Strategieberatung eine gemeinsame Action-Schnittstelle für menschliche Eingaben, Heuristik-KI und LLM-Auswahl schaffen. Nicht ausschließlich die bisherige PvEAI-Aktionsliste als alleinige Regelautorität übernehmen.

### Engine-Vertrag

Vorgeschlagene Schnittstellen; genaue Namen an die 0.1-Implementierung anpassen:

```python
get_visible_snapshot(actor_id) -> VisibleMatchSnapshot
get_legal_actions(actor_id) -> list[LegalAction]
validate_action(actor_id, action, expected_revision) -> ValidationResult
execute_action(actor_id, action, expected_revision) -> ActionResult
```

Die Aktion enthält alle Engine-Parameter einschließlich Ziel, Quelle und Karteninstanz. Die LLM gibt nur die action_id zurück; der Client löst diese ID auf die ursprüngliche Engine-Aktion auf.

- match_id muss pro Partie eindeutig sein, auch bei Retry.
- state_revision bei jeder relevanten Zustandsmutation erhöhen.
- Karten-/Dienerinstanzen eindeutig adressieren; Kartendefinitions-IDs und Anzeigenamen reichen bei Duplikaten nicht.
- action_id an Match, Revision, Akteur und aktuellen Entscheidungsrequest binden.
- Zug, Status, Mana, Ziele, Spott, Angriffslimits und Karteneffekte in der Engine prüfen.
- Ausführung nur nach erneutem atomarem Revisions-/Legalitätscheck.
- Antwort bei Profil-, Match-, Zug-, Revisions- oder Konfigurationswechsel verwerfen.
- Nach jeder ausgeführten Aktion Sieg/Niederlage prüfen; nach Matchende keine weitere LLM-/KI-Aktion.

### Sichtbarkeit

| Daten | Spielerberatung / Companion | Gegnerstrategie |
|---|---|---|
| Öffentliche Helden, Diener, Mana, Phase | Ja | Ja |
| Eigene Hand des jeweiligen Akteurs | Spielerhand | Gegnerhand |
| Hand des anderen Akteurs | Nein | Nein |
| Verdeckte Karten und geheime Effekte | Nur ausdrücklich öffentlich bekannte Informationen | Nur ausdrücklich öffentlich bekannte Informationen |
| Zukünftige Ziehreihenfolge / RNG-Zustand | Nein | Nein |
| Interne Profil-/Dateipfade und private Metadaten | Nein | Nein |

Companion- und Spielerberatungs-Snapshots nutzen dieselbe Spielerperspektive. Gegner-Snapshots separat aus Gegnerperspektive erstellen. Keine Serialisierung des vollständigen Player-, AppState- oder SaveGameData-Objekts.

Regeln und Kartentexte nur aus dem tatsächlich unterstützten und versionierten Spielinhalt beziehen. Unbekannte beziehungsweise nicht implementierte Mechaniken klar als nicht verfügbar markieren.

## 7. Strategieintegration

### Stufe A: Nur Vorschlag

1. Im eigenen Zug „Zug vorschlagen“ anklicken.
2. Sichtbaren Snapshot und legale Aktionen derselben Revision erzeugen.
3. Snapshot um request_id, Match-/Zugkontext und Regelversion ergänzen.
4. LLM genau eine action_id auswählen lassen.
5. JSON-Schema, ID, Request-Kontext und aktuelle Revision prüfen.
6. Vorschlag ohne automatische Zustandsänderung anzeigen.
7. Bei veraltetem Kontext Vorschlag entfernen; nicht stillschweigend neu ausführen.

### Beispiel für den Response-Vertrag

```json
{
  "type": "object",
  "properties": {
    "action_id": {"type": "string", "enum": ["a_1", "a_2", "a_3"]},
    "reason": {"type": "string", "maxLength": 240}
  },
  "required": ["action_id", "reason"],
  "additionalProperties": false
}
```

Das enum pro Anfrage aus den wirklich legalen Aktionen erstellen. Bei leerer Liste keine Modellanfrage starten; der Controller behandelt den Zustand. Eine optional mitgelieferte reason ist unzuverlässiger Modelltext, keine verbindliche Regelerklärung. Für einen Minimalmodus reason weglassen und eine geprüfte Engine-Aktionsbeschreibung anzeigen.

### Beispielrequest

```json
{
  "model": "qwen3:4b",
  "stream": false,
  "keep_alive": "2m",
  "format": {
    "type": "object",
    "properties": {
      "action_id": {"type": "string", "enum": ["a_1", "a_2"]}
    },
    "required": ["action_id"],
    "additionalProperties": false
  },
  "messages": [
    {"role": "system", "content": "Wähle genau eine action_id aus legal_actions. Erfinde keine Aktionen. Antworte ausschließlich im vorgegebenen JSON-Schema."},
    {"role": "user", "content": "{\"actor\":\"player\",\"state_revision\":12,\"legal_actions\":[{\"action_id\":\"a_1\",\"type\":\"play_card\",\"description\":\"Diener spielen\"},{\"action_id\":\"a_2\",\"type\":\"end_turn\"}]}"}
  ],
  "options": {"temperature": 0.2, "num_predict": 128}
}
```

Das Beispiel zeigt den Transportvertrag, keinen vollständigen Spielsnapshot. Produktiv das Snapshot-Objekt mit einem JSON-Serializer in messages.content übertragen; keine manuelle Stringverkettung. Parameter auf der eingesetzten Ollama-/Modellkombination testen. Für thinking-fähige Modelle think=false nach erfolgreicher Kompatibilitätsprüfung ergänzen, um lange interne Generierungen im Ersttest zu vermeiden.

### Stufe B: Ausführung auf Klick

- [ ] „Vorschlag ausführen“ erst nach gültigem Vorschlag anzeigen.
- [ ] Beim Klick Match, Akteur, Revision und Legalität erneut prüfen.
- [ ] Engine-Aktion aus dem serverlosen lokalen Action-Registry auflösen.
- [ ] Zustand ausschließlich durch die bestehende Engine verändern.
- [ ] Nach einer normalen Spieleraktion den vorherigen Vorschlag sofort invalidieren.

### Stufe C: Optionaler Gegner

Pro Entscheidung einen neuen gegnerspezifischen Snapshot und neue legale Aktionen bilden. Nicht einen gesamten Zug mit veralteten IDs vorab planen lassen. Maximal 15 Aktionen und ein gemeinsames 10-Sekunden-Startbudget pro Zug; danach restlichen Zug mit Heuristik-KI abschließen. EndTurn und Matchende brechen die Schleife ab.

Heuristischer Fallback nutzt dieselbe Engine-Validierung. Modellantworten dürfen nicht unmittelbar die bisherige AI-execute_action-Methode unter Umgehung des zentralen Validators aufrufen.

## 8. Companion und UI

### Companion-Funktion

- Deutschsprachiger Rook mit kurzem, hilfsbereitem und leicht sarkastischem Stil.
- Nutzerfragen zu sichtbarem Board und implementierten Regeln.
- Keine erfundenen Quests, Belohnungen oder verbindlichen Regelzusagen.
- Bei fehlenden Regelinformationen ausdrücklich Unsicherheit nennen.
- Startversion nur manuelle Chatfragen; keine LLM-Anfrage nach jedem Kampfevent.
- Optionale vorbereitete lokale Statussätze bei Offlinebetrieb.

### Kontextmanagement

- Geprüfte Regeln in resources/rules_de.md mit Regelversion und unterstützten Mechaniken.
- Maximal sechs letzte Nutzer-/Assistant-Paare und ein aktueller sichtbarer Snapshot.
- Zusätzlich Gesamtzeichenlimit, beispielsweise 12.000 Zeichen für History; alte vollständige Paare zuerst entfernen.
- Eingabe maximal 1.000 Zeichen; sichtbare Ausgabe beispielsweise auf 1.500 Zeichen begrenzen.
- num_predict zunächst 256; Prompt und Kontextgröße auf der Zielhardware messen.
- Chatverlauf nur im Arbeitsspeicher, nach Profil-/Matchwechsel löschen; keine automatische Persistenz.
- Fehlschlag oder abgebrochene Antwort nicht als erfolgreiches Assistant-Turn in die Historie aufnehmen.

Diese Limits sind vorgeschlagene Startwerte. Zeichenlimits ersetzen keine Modell-Tokenmessung.

### UI-Anbindung

GameBoard um ein einklappbares Companion-Panel und eine kleine LLM-Statusanzeige erweitern. Kampflog und Chat bleiben getrennt. LLM-Text als normalen Text darstellen; keine Ausführung von HTML, Code, Links oder Tool-Aufrufen aus Modellantworten.

„Zug vorschlagen“ und „Vorschlag ausführen“ als zusätzliche Kampfaktionen integrieren, nicht als neue Hauptmenüpunkte. Während einer Anfrage nur betroffene LLM-Bedienelemente deaktivieren; normale Spieleraktionen bleiben möglich und invalidieren gegebenenfalls den Snapshot.

Falls später Streaming ergänzt wird: REST-Streaming verarbeitet JSON-Zeilen; content nur gedrosselt rendern und thinking nicht als Companion-Ausgabe anzeigen. Auch jeder Teilchunk braucht eine gültige Session-/Match-Zuordnung. Grundlage: [Ollama Streaming](https://docs.ollama.com/capabilities/streaming).

## 9. Lifecycle, Ressourcen und Datenschutz

### Lifecycle

- [ ] AppService besitzt den HTTP-Client und schließt ihn am Appende.
- [ ] Jede Anfrage trägt request_id, profile_id, match_id, state_revision und config_generation intern.
- [ ] Interne IDs nur soweit für die Modellaufgabe nötig in den Prompt übernehmen.
- [ ] GameBoard-Verlassen, Retry, Matchende und Profilwechsel invalidieren aktive und wartende Requests.
- [ ] Keine UI-Updates auf entfernten Controls.
- [ ] Alte Antwort nicht auf einen neuen Match mit ähnlichem Zustand übertragen.
- [ ] Matchende während laufender Anfrage ohne Verzögerung darstellen.

### Ressourcen

Die Queue begrenzt gleichzeitige Generierung, garantiert aber nicht, dass nur ein Modell im Speicher bleibt. keep_alive steuert die gewünschte Modellresidenz; tatsächliches Verhalten und Speicherverbrauch messen. Nutzer dürfen Modelle auch außerhalb von Merithra verwenden: keine ungefragte globale Entladung oder Beendigung des Ollama-Dienstes.

Kaltstart und warme Antworten separat messen. Niedrige Temperatur und feste Seeds können Tests unterstützen, ersetzen aber keine deterministische Engine; LLM-Antworten nicht als deterministisch bezeichnen.

### Datenschutz und Sicherheit

- Nur Loopback-Kommunikation und bewusst lokal getestete Modelle.
- Keine externen API-Keys, Telemetrie oder Cloud-Aufrufe in diesem Meilenstein.
- Keine automatisch geladenen URLs oder Dateien aus Chats.
- Companion hat keinerlei Tools oder Zustands-Schreibrechte.
- Prompt-Injection in Nutzertext oder Kartentext darf Regeln/Engine-Zugriff nicht verändern.
- Technische Logs enthalten Status, Dauer, Modellkennung und Fehlerkategorie, nicht Chattext, Profilnamen, Handkarten oder vollständige Prompts.
- Prompt-/Antwortdump nur als ausdrücklicher späterer Debugmodus; für Preview standardmäßig nicht vorhanden.

## 10. Meilensteine und Aufwände

Schätzungen in konzentrierten Entwicklertagen. Keine fest zugesagten Termine; zusätzliche Engine-Lücken können den Aufwand erhöhen.

| ID | Arbeitspaket | Konkrete Umsetzung | Abnahme | Aufwand |
|---|---|---|---|---|
| M-LLM-00 | 0.1-Schnittstellen prüfen | Navigation, Settings, Cleanup, MatchManager und Teststand prüfen; tatsächliche Importpfade dokumentieren. | Keine doppelte App-/Kampfsteuerung; Erweiterungspunkte bestätigt. | 0,5–1 Tag |
| M-LLM-01 | Aktionen und Snapshots | Eindeutige Match-/Instanz-IDs, Revision, gemeinsamer Validator und Perspektivfilter. | Mensch, Heuristik und Beratung nutzen denselben Action-Vertrag; keine geheimen Daten. | 1,5–3 Tage |
| M-LLM-02 | Ollama-Provider | Asynchroner Client, tags/chat, Schema-Parsing, Gesamtdeadlines, Fehlerklassen und FakeProvider. | Tests ohne Ollama; echte kurze lokale Anfrage funktioniert. | 1–2 Tage |
| M-LLM-03 | Optionen und Lifecycle | Settings ergänzen, Verbindungstest, Queue, Cancel/Invalidierung und Statusanzeige. | Menü/Kampf ohne Ollama nutzbar; Profil-/Matchwechsel sicher. | 1–2 Tage |
| M-LLM-04 | Companion | Regeln, versionierte Prompts, begrenzte Historie und einklappbares Panel. | Deutsche Antwort auf sichtbaren Zustand; keine Schreibaktionen. | 1–2 Tage |
| M-LLM-05 | Zugberatung | action_id-Schema, Vorschlagsanzeige, Revisionstest und erneute Validierung auf Klick. | Vorschlag verändert nichts; Ausführung nur legal und aktuell. | 1,5–3 Tage |
| M-LLM-06 | Optionaler LLM-Gegner | Pro-Aktion-Auswahl, Gesamtbudget, Aktionlimit und heuristischer Fallback. | Vollständige Partie mit und ohne Ollama; keine Aktion nach Matchende. | 1–2 Tage |
| M-LLM-07 | Qualität und Preview | Regressionen, reale Hardwaremessung, Offline-Smoke-Test und Setup-/Release-Dokumentation. | Release-Checkliste erfüllt; bekannte Einschränkungen dokumentiert. | 1–2 Tage |

Grobe Gesamtspanne: 8–15 Entwicklertage für die verbindliche Preview, 9–17 mit optionalem LLM-Gegner. Die obere Grenze setzt voraus, dass keine größeren noch offenen 0.1-/Regelprobleme hinzukommen. Werte sind gerundete Planungsspannen.

Empfohlene Reihenfolge: M-LLM-00 → 01 → 02 → 03 → 04 → 05 → 07. M-LLM-06 erst nach stabiler Beratung einschieben oder separat ausliefern.

## 11. Tests und Qualitätsnachweise

### Standardtests ohne Ollama

FakeProvider liefert kontrollierte Antworten und Fehler; Standard-CI benötigt weder Modell-Download noch GPU noch laufenden Dienst.

- [ ] Gültige action_id wird korrekt aufgelöst.
- [ ] Ungültiges JSON, falsche Felder, zusätzliche Felder und unbekannte action_id werden abgelehnt.
- [ ] Ungültige/veraltete Antworten verändern keinen Zustand.
- [ ] Antwort nach Profilwechsel, Retry, Matchende oder Navigation wird verworfen.
- [ ] Spieler-/Gegnerperspektive enthält niemals die Hand des anderen Akteurs.
- [ ] Keine RNG-Zustände oder zukünftigen Ziehreihenfolgen im Prompt.
- [ ] Doppelklick, Queue-Limit, Budgetablauf, Reparaturversuch und Circuit-Breaker.
- [ ] Normale Spieleraktion während Beratung invalidiert den Vorschlag.
- [ ] Regeln und Kartendaten als Daten behandeln; Prompt-Injection kann keine Aktionen freischalten.
- [ ] Chat-History bleibt begrenzt und wird korrekt zurückgesetzt.
- [ ] Settings-Migration übernimmt bestehende 0.1-Konfiguration mit LLM aus als Default.
- [ ] Fallback führt nur gültige Aktionen aus und stoppt bei Sieg/Niederlage.
- [ ] Vorhandene 0.1-Tests bleiben erfolgreich.

### Echte Integrationstests

Eigene pytest-Markierung ollama_integration; nur auf ausdrücklichen Aufruf ausführen. Nicht exakte Formulierungen oder stets identische Strategieauswahl erwarten.

```bash
pytest -m "not ollama_integration"
pytest -m ollama_integration
```

- [ ] Modellliste und Modellkennung werden korrekt erkannt.
- [ ] Kurze deutsche Companion-Antwort wird empfangen.
- [ ] Dynamisches action_id-Schema wird eingehalten oder sicher abgewiesen.
- [ ] Ollama während Anfrage stoppen: Timeout/Fallback statt Appabsturz.
- [ ] Netzwerkzugang nach Modellinstallation deaktivieren: lokaler Betrieb funktioniert.
- [ ] Kaltstart, warmer Request und Modellwechsel separat testen.

### Messplan

Mindestens 30 warme Requests pro Rolle auf einer dokumentierten Zielkonfiguration messen und zusätzlich mehrere Kaltstarts erfassen. Festhalten: Betriebssystem, CPU, RAM, GPU/VRAM, Ollama-Version, Modellkennung/Digest, Parameter, Median/P95-Latenz, Fehlerrate und Timeout-Anteil.

Transport-/API-Metriken bei Erfolg erfassen; Ollama liefert entsprechende Laufzeit-/Tokeninformationen. Grundlage: [Ollama Usage](https://docs.ollama.com/api/usage).

Qualität anhand vorbereiteter Boards bewerten: legale Auswahl, Spottbeachtung, direkte Siegchance, unzureichendes Mana, volle Dienerreihe und Matchende. Die Engine verhindert Regelverstöße; das Modell muss nicht alle Taktikfälle perfekt lösen. Keine „bessere KI“-Behauptung ohne Vergleich zur Heuristik veröffentlichen.

## 12. Definition of Done

- [ ] 0.1-Startbildschirm, Anmeldung und Hauptmenü unverändert nutzbar.
- [ ] LLM standardmäßig aus und ohne Internet/Account optional.
- [ ] Aktivierte LLM erkennt fehlenden Dienst/Modell ohne Blockade des Spielflusses.
- [ ] Companion erklärt nur bereitgestellte implementierte Regeln und sichtbare Zustände.
- [ ] Strategie wählt ausschließlich aus Engine-Aktionen; Engine validiert erneut.
- [ ] Veraltete Antworten, Doppelklicks und Navigation erzeugen keine falschen Aktionen.
- [ ] Alle Fehlerpfade erlauben normales Weiterspielen oder Heuristik-Fallback.
- [ ] Keine direkten Modell-Schreibzugriffe auf Kampf oder persistenten Fortschritt.
- [ ] Kein fremdes Profil und keine versteckten Gegnerinformationen im Kontext.
- [ ] Mock-Tests und reale Smoke-Tests erfolgreich dokumentiert.
- [ ] Latenz-/Speichermessungen auf mindestens einer tatsächlichen Zielhardware vorhanden.
- [ ] SETUP.md, LLM_INTEGRATION.md, ARCHITECTURE.md und TESTING.md abgeglichen.
- [ ] Preview-Version und Einschränkungen dokumentiert; optionaler Gegnermodus nur nach eigener Abnahme sichtbar.

## 13. Konkrete Arbeitstickets

1. refactor: unify legal actions and perspective-safe match snapshots
2. feat: add asynchronous local ollama provider and fake provider
3. feat: extend options with local llm settings and connection checks
4. feat: add request lifecycle invalidation and llm status ui
5. feat: add rook companion with bounded local chat context
6. feat: add validated player move suggestions
7. feat: add optional llm opponent with heuristic fallback
8. test: cover llm failures privacy and stale response handling
9. docs: document local llm setup benchmarks and preview limitations

Erste lauffähige Zwischenabnahme: Nach M-LLM-03 kann der Nutzer Ollama in den bestehenden Optionen prüfen und weiterhin uneingeschränkt ohne LLM spielen. Erst danach Chat und Strategie im GameBoard aktivieren.
