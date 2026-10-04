# Merithra - API-Spezifikation

## Versionsverwaltung
- **Version:** 1.0 (Foundation Phase - Local First)
- **Status:** Entwurf
- **Zuletzt aktualisiert:** 2026-10-03

---

## 1. API-Philosophie

### 1.1 Grundsätze
- **Local-First:** MVP vollständig offline spielbar, Network-Layer optional
- **RESTful Design:** Falls Server-Implementation nötig
- **OpenAPI 3.0:** Generierte Dokumentation und Client-Stubs
- **Versionierte Endpoints:** `/v1/`, `/v2/` für Breaking Changes
- **LLM Local Provider:** Alle KI-Kommunikation erfolgt lokal über Ollama, keine externen API-Kosten

### 1.2 Zugriffs-Modi
| Modus | Beschreibung |
|-------|--------------|
| **Offline** | Vollständiges Spiel, lokale Speicherung (SQLite) |
| **LAN** | Local Multiplayer, keine Account-Synchronisation |
| **Online** | Account-basiert, Cloud-Sync, Multiplayer |

---

## 2. API-Endpoints (Geplant)

### 2.1 Authentifizierung (Phase 4+)
| Endpoint | Method | Beschreibung | Auth |
|----------|--------|--------------|------|
| `POST /api/v1/auth/register` | POST | Neuen Account registrieren | Public |
| `POST /api/v1/auth/login` | POST | Login mit E-Mail/Passwort | Public |
| `POST /api/v1/auth/refresh` | POST | JWT Token refreshen | Public |
| `POST /api/v1/auth/logout` | POST | Logout, Token invalidieren | Bearer |

### 2.2 Account & Collection
| Endpoint | Method | Beschreibung | Auth |
|----------|--------|--------------|------|
| `GET /api/v1/accounts/me` | GET | Aktuellen Account-Daten abrufen | Bearer |
| `GET /api/v1/collections` | Sammlung auflisten | Bearer |
| `POST /api/v1/collections/craft` | Karte craften | Bearer |
| `POST /api/v1/collections/disenchant` | Karte zerstäuben | Bearer |

### 2.3 Kampagne & PvE
| Endpoint | Method | Beschreibung | Auth |
|----------|--------|--------------|------|
| `GET /api/v1/pve/chapters` | Kapitel auflisten | Bearer |
| `GET /api/v1/pve/chapters/{id}` | Kapitel-Details | Bearer |
| `GET /api/v1/pve/missions` | Missionen auflisten | Bearer |
| `POST /api/v1/pve/runs` | Run starten | Bearer |
| `POST /api/v1/pve/runs/{id}/complete` | Run abschließen | Bearer |

### 2.4 Gilden
| Endpoint | Method | Beschreibung | Auth |
|----------|--------|--------------|------|
| `GET /api/v1/guilds` | Gilden auflisten | Bearer |
| `POST /api/v1/guilds` | Gilde gründen | Bearer |
| `GET /api/v1/guilds/{id}` | Gilden-Details | Bearer |
| `POST /api/v1/guilds/{id}/join` | Gilde beitreten | Bearer |
| `POST /api/v1/guilds/{id}/raid` | Raid starten | Bearer |

### 2.5 PvP
| Endpoint | Method | Beschreibung | Auth |
|----------|--------|--------------|------|
| `GET /api/v1/pvp/ladder` | Rangliste anzeigen | Bearer |
| `POST /api/v1/pvp/queue` | Queue für Rangliste | Bearer |
| `GET /api/v1/pvp/arena` | Arena-Infos | Bearer |
| `POST /api/v1/pvp/invite` | Freundschaftsspiel einladen | Bearer |

### 2.6 Spiel-Zustand (WebSocket)
| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `ws://server/api/v1/ws/{game_id}` | WebSocket | Echtzeit-Zustands-Synchronisation |

**WebSocket-Nachrichten:**
- `{"type": "move", "action": "play_card", "card_id": "..."}`
- `{"type": "move", "action": "attack", "target_id": "..."}`
- `{"type": "state", "game_state": {...}}`
- `{"type": "error", "message": "..."}`

---

## 3. Request/Response Formate

### 3.1 JSON-Standard
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-10-03T10:00:00Z",
    "version": "1.0"
  }
}
```

### 3.2 Fehler-Handling
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Ungültige Eingabe",
    "details": { "field": "mana", "reason": "Nicht genug Mana" }
  }
}
```

**HTTP-Status-Codes:**
- `200` OK
- `201` Created
- `400` Bad Request (Validierungsfehler)
- `401` Unauthorized (kein Token)
- `403` Forbidden (kein Zugriff)
- `404` Not Found
- `429` Too Many Requests (Rate Limit)
- `500` Internal Server Error

---

## 4. Rate Limiting

| Endpoint | Limit | Zeitfenster |
|----------|-------|-------------|
| `/auth/login` | 5 attempts | pro Minute |
| `/pvp/queue` | 3 requests | pro Minute pro User |
| `/pve/runs` | 10 requests | pro Stunde pro User |
| `/* (all)` | 100 requests | pro Minute pro IP |

---

## 5. WebSocket-Protokoll (Detail)

### 4.1 Nachrichten-Format
```json
{
  "type": "ACTION",
  "player_id": "string",
  "game_id": "string",
  "payload": { ... }
}
```

### 4.2 Typen
- `MOVE`: Spieleraktion (Karte spielen, Angriff)
- `STATE`: Game State Update (für Replays/Synchronisation)
- `ERROR`: Fehlermeldung
- `SYNC`: Initial State Sende nach Verbindung

### 4.3 Authoritative Model
- **Server-authoritative für:** PvP, Gilden-Raids, Fortschrittsspeicherung
- **Client-authoritative für:** Singleplayer Kampagne, lokale Ansichten

---

## 6. Datei-Uploads (Karten-Editor, Assets)

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `POST /api/v1/assets/card-art` | POST | Karten-Artwork hochladen (multipart/form-data) |
| `POST /api/v1/tools/cards` | POST | Neue Karte ins System hinzufügen |

**Authentifizierung:** Admin/Moderator-Rechte nötig

---

## 7. OpenAPI Generierung

### 6.1 Konfiguration
```python
# fastapi Generierung
app = FastAPI(
    title="Merithra API",
    version="1.0.0",
    description="API für Merithra Kartenspiel",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

### 6.2 Client-Stubs
- **Python:** `pip install openapi-pygenerator` oder manuell
- **TypeScript/Angular:** `openapi-generator-cli generate`
- **Swift/Kotlin:** Für mobile Clients

---

## 7. API-Entwicklungs-Phasen

### Phase 1 (MVP - Local)
- Kein Server-API nötig
- Alle Daten in lokaler SQLite
- Interne Python-Module als "API"

### Phase 2 (Singleplayer + Offline-Multiplayer)
- Optionale REST-Endpoints für Local Network
- Save/Load via API-ähnliche Struktur

### Phase 3 (Online-Multiplayer)
- Vollständiges REST + WebSocket API
- Authentifizierung & Rate Limiting
- Cloud-Synchronisation

### Phase 4 (Live Service)
- Erweiterte Endpoints (Events, Statistics)
- Versionierung v2.0 für Breaking Changes
- Webhooks für Events (Guild-Updates, Finish-Belohnungen)

---

## 8. Offene API-Fragen

- [ ] **Auth-Workflow:** OAuth2 vs JWT vs Session-Cookie?
- [ ] **Datenkomprimierung:** JSON vs MessagePack für WebSocket?
- [ ] **File Storage:** Lokal vs S3 vs Cloudinary für Assets?
- [ ] **WebSocket Library:** `websockets` vs `aiohttp` vs `socket.io`?
- [ ] **API Versionierung:** URL-Path (`/v1/`) vs Header Accept-Version?

## 9. LLM Local Provider (Ollama)

### 9.1 Endpoint
- `POST http://127.0.0.1:11434/api/chat`
- Alle KI-Kommunikation erfolgt lokal, keine externen Kosten

### 9.2 Request-Format (Strategy Agent)
```json
{
  "model": "qwen3:4b",
  "stream": false,
  "format": "json",
  "messages": [
    {
      "role": "system",
      "content": "Du bist ein Kartenspiel-Strategie-Agent. Wähle ausschließlich eine Aktion aus legalActions. Antworte ausschließlich als JSON."
    },
    {
      "role": "user",
      "content": JSON.stringify({
        "state": { ... },
        "legalActions": [ ... ]
      })
    }
  ],
  "options": {
    "temperature": 0.3,
    "num_predict": 160
  }
}
```

### 9.3 Request-Format (Companion Agent)
```json
{
  "model": "llama3.2:3b",
  "stream": false,
  "messages": [
    {
      "role": "system",
      "content": "Du bist Rook, ein sarkastischer, hilfsbereiter Kartenmeister. Du erfindest keine Regeln und verrätst keine verdeckten Karten."
    },
    {
      "role": "user",
      "content": "Warum soll ich den Golem mit Fireball töten?"
    }
  ],
  "options": {
    "temperature": 0.7,
    "num_predict": 220
  }
}
```

### 9.4 Verfügbare Modelle
- **Strategie:** `qwen3:4b` (2,5-2,6 GB), `qwen3:8b` (5,2 GB)
- **Konversation:** `llama3.2:3b` (2,0 GB), `qwen3:4b` als Alternative

### 9.5 Fehler-Behandlung
- Ollama nicht erreichbar → KI-Funktionen deaktivieren, Spiel normal fortsetzen
- Modell nicht installiert → Installationshinweis anzeigen
- Ungültiges JSON → Request wiederholen oder Fallback-Aktion wählen
- Illegaler Zug → Zug verwerfen, neue Auswahl aus legalen Aktionen anfordern

---

*Dokument-Version: 1.0*  
*Status: Foundation Phase*  
*Erstellt: 2026-10-03*