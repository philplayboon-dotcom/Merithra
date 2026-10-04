# LLM_INTEGRATION.md

## Ziel

Das Kartenspiel erhält eine lokale, kostenlose KI-Integration. Die KI ist **kein Bestandteil der autoritativen Spiellogik**, sondern übernimmt zwei klar getrennte Aufgaben:

1. **Strategie-Agent:** schlägt Spielzüge vor und begründet sie.
2. **Companion-LLM:** führt Konversationen mit dem Spieler, erklärt Züge, gibt Tipps und verkörpert eine Spielfigur.

Die Spiel-Engine bleibt allein verantwortlich für Regeln, Karten-Effekte, Mana, Angriffe, RNG, Spielzustand und Sieg/Niederlage.

## Grundprinzip

Die LLM erhält ausschließlich den für sie relevanten Spielzustand und wählt aus einer Liste **legaler Aktionen**. Die Spiel-Engine validiert jeden Vorschlag, bevor er ausgeführt wird.

```text
Spielzustand
   ↓ strukturiert als JSON
Strategie-LLM
   ↓ schlägt Zug vor
Regel-Engine
   ↓ validiert Legalität und Effekte
Spiel führt Zug aus
```

Die Bilderkennung wird für Spielzüge nicht benötigt. Das Spiel kennt den Zustand intern und kann ihn präzise als JSON übergeben. Dadurch sind die Modelle kleiner, schneller und zuverlässiger.

## Empfohlene Architektur

### Strategie-Agent

Der Strategie-Agent erhält den aktuellen Spielzustand und eine Liste erlaubter Aktionen.

Aufgaben:

- Karte spielen
- Angriff wählen
- Heldenfähigkeit einsetzen
- Zug beenden
- Ziel priorisieren
- Begründung liefern

Empfohlenes Modell:

- **Qwen3 4B Q4_K_M**
- Downloadgröße: etwa 2,5–2,6 GB
- Ollama-Tag: `qwen3:4b`
- Alternative für stärkere Qualität: `qwen3:8b`, etwa 5,2 GB

Der Agent antwortet ausschließlich mit strukturiertem JSON. Temperatur sollte niedrig sein, etwa `0.2` bis `0.4`.

### Companion-LLM

Die Companion-LLM spricht mit dem Spieler.

Aufgaben:

- Konversation
- Erklärung von Zügen
- Tutorial und Regelfragen
- Persönlichkeit und Rollenspiel
- Kommentare zum Spielverlauf
- Hinweise, ohne verdeckte Informationen preiszugeben

Empfohlenes Modell:

- **Llama 3.2 3B Q4**
- Downloadgröße: etwa 2,0 GB
- Ollama-Tag: `llama3.2:3b`
- Alternative: ebenfalls `qwen3:4b`, wenn nur ein Modell unterstützt werden soll

Die Companion-LLM darf keine verdeckten Karten, Gegner-Handkarten oder internen RNG-Werte sehen.

## Empfohlene Modellkombination

| Rolle | Modell | Festplatte | Zweck |
|---|---|---:|---|
| Strategie | Qwen3 4B Q4_K_M | 2,5–2,6 GB | Spielzüge, Board-Bewertung, Aktionen |
| Konversation | Llama 3.2 3B Q4 | 2,0 GB | Chat, Erklärungen, Persönlichkeit |
| **Gesamt** |  | **4,5–4,6 GB** | Empfohlenes Standard-Paket |

Alternative:

| Paket | Modelle | Festplatte | Einsatz |
|---|---|---:|---|
| Minimal | Qwen3 4B | 2,5–2,6 GB | Ein Modell für Strategie und Chat |
| Empfohlen | Qwen3 4B + Llama 3.2 3B | 4,5–4,6 GB | Getrennte Spezialmodelle |
| Besser | Qwen3 8B + Llama 3.2 3B | 7,2 GB | Stärkere Strategiequalität |
| Premium | Qwen3 8B Q8 + Llama 3.2 3B | 10,7 GB | Nur für leistungsstarke PCs |

## Installation

Der Spieler installiert Ollama und lädt die gewünschten Modelle herunter.

```bash
# Empfohlenes Duo: etwa 4,5 GB
ollama pull qwen3:4b
ollama pull llama3.2:3b

# Alternative mit stärkerer Strategie: etwa 7,2 GB
ollama pull qwen3:8b
ollama pull llama3.2:3b
```

Die installierten Modelle lassen sich prüfen mit:

```bash
ollama list
```

## Systemanforderungen

Die Festplatte ist bei diesen Modellgrößen selten das Problem. Entscheidend sind RAM beziehungsweise VRAM und die gewünschte Antwortgeschwindigkeit.

| Hardware | Empfehlung | Erfahrung |
|---|---|---|
| 8 GB RAM, CPU only | Qwen3 0.6B/1.7B oder Llama 3.2 1B | Chat möglich, Strategie nur einfach |
| 16 GB RAM, CPU only | Qwen3 4B Q4 | Funktionsfähig, aber langsamer |
| GPU mit 4–6 GB VRAM | Qwen3 4B + Llama 3.2 3B | Guter Einstieg |
| GPU mit 8 GB VRAM | Qwen3 8B + Llama 3.2 3B | Gute Balance aus Qualität und Geschwindigkeit |
| GPU mit 12 GB VRAM | Qwen3 14B Q4 | Deutlich bessere Planung, aber weniger verbreitet |

Für das empfohlene Duo sollten Spieler mindestens **16 GB RAM** und idealerweise eine GPU mit **6 GB VRAM** haben. Wer nur ein Modell nutzt, kommt mit Qwen3 4B auch mit weniger Ressourcen aus.

## Festplattenbedarf

| Komponente | Speicherbedarf |
|---|---:|
| Qwen3 4B Q4_K_M | 2,5–2,6 GB |
| Llama 3.2 3B Q4 | 2,0 GB |
| Qwen3 8B Q4_K_M | 5,2 GB |
| Qwen3 8B Q8 | 8,7 GB |
| Ollama-Installation und Cache | ungefähr 1–2 GB |

Empfohlene freie Festplattenkapazität:

- **8 GB** für das Standard-Paket mit Qwen3 4B und Llama 3.2 3B.
- **12 GB** für das Paket mit Qwen3 8B und Llama 3.2 3B.

## API-Anbindung

Das Spiel kommuniziert lokal mit Ollama:

```text
http://127.0.0.1:11434/api/chat
```

Dadurch entstehen:

- keine API-Kosten,
- keine Anfragelimits,
- keine Abhängigkeit von einem Cloud-Anbieter,
- keine Übertragung von Spieldaten ins Internet,
- Offline-Fähigkeit nach Modell-Download.

## Beispiel: Strategie-Request

```ts
const response = await fetch("http://127.0.0.1:11434/api/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    model: "qwen3:4b",
    stream: false,
    format: "json",
    messages: [
      {
        role: "system",
        content:
          "Du bist ein Kartenspiel-Strategie-Agent. Wähle ausschließlich eine Aktion " +
          "aus legalActions. Antworte ausschließlich als JSON."
      },
      {
        role: "user",
        content: JSON.stringify({
          state: {
            turn: 8,
            myMana: 5,
            myHealth: 21,
            enemyHealth: 14,
            myBoard: [
              { id: "wolf", attack: 3, health: 2, canAttack: true }
            ],
            enemyBoard: [
              { id: "golem", attack: 4, health: 5, taunt: true }
            ],
            hand: [
              { id: "fireball", cost: 4 },
              { id: "bear", cost: 5 }
            ],
            legalActions: [
              { type: "attack", attacker: "wolf", target: "golem" },
              { type: "play_card", card: "fireball", target: "golem" },
              { type: "play_card", card: "bear" },
              { type: "end_turn" }
            ]
          }
        })
      }
    ],
    options: {
      temperature: 0.3,
      num_predict: 160
    }
  })
});

const data = await response.json();
const decision = JSON.parse(data.message.content);
```

Erwartete Antwort:

```json
{
  "action": "play_card",
  "card": "fireball",
  "target": "golem",
  "confidence": 0.82
}
```

## Beispiel: Companion-Request

```ts
const response = await fetch("http://127.0.0.1:11434/api/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    model: "llama3.2:3b",
    stream: false,
    messages: [
      {
        role: "system",
        content:
          "Du bist Rook, ein sarkastischer, hilfsbereiter Kartenmeister. " +
          "Du erfindest keine Regeln und verrätst keine verdeckten Karten."
      },
      {
        role: "user",
        content:
          "Warum soll ich den Golem mit Fireball töten?"
      }
    ],
    options: {
      temperature: 0.7,
      num_predict: 220
    }
  })
});

const data = await response.json();
const answer = data.message.content;
```

## Sicherheits- und Stabilitätsregeln

- Die LLM darf **niemals** direkt den Spielzustand verändern.
- Jeder Zugvorschlag muss durch die Regel-Engine validiert werden.
- Die LLM erhält nur Informationen, die der jeweilige Spieler sehen darf.
- Versteckte Karten, Gegner-Handkarten und RNG-Zustände gehören nicht in den Prompt.
- Bei ungültigen Antworten: einmal erneut anfragen, danach Fallback-Aktion wählen.
- Bei nicht laufendem Ollama: KI-Funktionen deaktivieren oder vorbereitete Dialoge verwenden.
- Antworten begrenzen, etwa 120–220 Tokens, um die Latenz niedrig zu halten.
- Für Strategie niedrige Temperatur verwenden; für Konversation höhere Temperatur.

## Fehlerbehandlung

| Problem | Reaktion |
|---|---|
| Ollama läuft nicht | KI-Chat ausblenden, Spiel normal weiterführen |
| Modell nicht installiert | Installationshinweis anzeigen |
| Modell zu langsam | Kleineres Modell empfehlen |
| Ungültiges JSON | Request wiederholen oder Fallback-Zug wählen |
| Illegaler Zug | Zug verwerfen, neue Auswahl aus legalen Aktionen anfordern |
| Keine GPU | CPU-Modus mit kleinerem Modell anbieten |

## Entwicklungsmodus: lokal

Während der Entwicklung wird ausschließlich eine lokale LLM über Ollama verwendet. Dadurch entstehen keine API-Kosten, keine Anfragelimits und keine Abhängigkeit von einem Cloud-Anbieter.

Empfohlenes Entwicklungs-Setup:

```bash
ollama pull qwen3:4b
ollama pull llama3.2:3b
```

- **Qwen3 4B Q4** übernimmt Spielzüge, Strategie und strukturierten JSON-Output.
- **Llama 3.2 3B Q4** übernimmt Konversationen, Erklärungen und die Persönlichkeit des Companions.
- Alle Requests laufen über `http://127.0.0.1:11434/api/chat`.
- Die Regel-Engine validiert jeden vorgeschlagenen Spielzug unabhängig von der LLM.

## Spätere Cloud-Integration: DeepSeek V3

Nach der lokalen Entwicklungsphase kann optional **DeepSeek V3** als online gehostete Produktions- oder BYOK-Option integriert werden. DeepSeek V3 eignet sich als gemeinsames Modell für Strategie-Agent und Companion, sodass zunächst kein zweiter Cloud-Provider erforderlich ist.

Die Integration sollte über einen austauschbaren Provider-Adapter erfolgen, vorzugsweise über eine OpenAI-kompatible Schnittstelle wie OpenRouter:

```text
Spiel
  ├── LocalProvider    → Ollama / qwen3:4b / llama3.2:3b
  └── CloudProvider    → OpenRouter / DeepSeek V3
```

Empfohlene Betriebsarten:

| Modus | Anbieter | Modell | Zweck |
|---|---|---|---|
| Entwicklung | Ollama lokal | Qwen3 4B + Llama 3.2 3B | Kostenlose Entwicklung ohne Limits |
| Spieler mit eigener Hardware | Ollama lokal | Qwen3 4B + Llama 3.2 3B | Offline und privat |
| Spätere Online-Option | OpenRouter / eigener DeepSeek-Zugang | DeepSeek V3 | Gute Qualität für Strategie und Chat |
| Spielerfinanzierte Online-Option | BYOK | DeepSeek V3 | Jeder Spieler verwendet seinen eigenen API-Key und sein eigenes Guthaben |

Für DeepSeek V3 sollten zwei getrennte Prompt-Profile bestehen:

- **Strategie:** niedrige Temperatur (`0.2` bis `0.4`), striktes JSON, kurze Antworten, ausschließlich `legalActions` auswählen.
- **Companion:** höhere Temperatur (etwa `0.6` bis `0.8`), Persönlichkeit, sichtbarer Spielzustand und begrenzte Gesprächshistorie.

Der Cloud-Provider darf die lokale Integration nicht ersetzen, sondern nur ergänzen. Das Spiel muss weiterhin ohne Account, API-Key und Internet mit der lokalen Ollama-Variante funktionieren.

### DeepSeek-V3-Kostenkontrolle

Für die spätere Integration sind diese Schutzmaßnahmen verpflichtend:

- API-Key niemals im Client hartcodieren oder öffentlich ausliefern.
- Bei zentralem Betrieb den API-Zugriff über ein eigenes Backend leiten und pro Spieler Limits setzen.
- Bei BYOK den API-Key nur lokal und verschlüsselt speichern.
- Spielzustand stark komprimieren; keine Screenshots und keine vollständige Spielhistorie senden.
- Strategieantworten auf etwa 80–150 Output-Tokens beschränken.
- Companion-Antworten auf etwa 150–250 Output-Tokens beschränken.
- Wiederkehrende System-Prompts und Regeltexte cachen, sofern der gewählte Provider Prompt-Caching unterstützt.
- Requests bei Fehlern, Rate Limits oder Budgetüberschreitungen auf die lokale LLM oder einen spielinternen Fallback zurückführen.

## Optionale Erweiterung: BYOK

Neben der lokalen Lösung kann das Spiel optional „Bring Your Own Key“ unterstützen.

Mögliche Anbieter:

- OpenRouter
- Hugging Face Inference Providers
- Cloudflare Workers AI

Dabei trägt jeder Spieler seinen eigenen API-Key ein. Das Spiel speichert den Key nur lokal und verschlüsselt. Der Spieler übernimmt damit Kosten, Limits und Datenschutzentscheidungen selbst.

Diese Option ist sinnvoll für Spieler ohne ausreichende Hardware, sollte aber nicht Voraussetzung für das Spiel sein.

## Fazit

Für ein Hearthstone-ähnliches Kartenspiel ist folgende Reihenfolge vorgesehen:

- **Jetzt in der Entwicklung:** Ollama lokal, Qwen3 4B Q4 für Spielzüge und Llama 3.2 3B Q4 für Konversationen.
- **Später optional online:** DeepSeek V3 über einen austauschbaren OpenAI-kompatiblen Provider-Adapter.
- **Keine Bilderkennung** für normale Spielzüge; der Spielzustand wird strukturiert als JSON übermittelt.
- **Regel-Engine** bleibt die alleinige autoritative Instanz.
- **Lokaler Festplattenbedarf:** etwa 4,5–4,6 GB für beide Standardmodelle.
- **Lokaler Betrieb:** keine API-Kosten und keine Anfragelimits.
