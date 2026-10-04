# Merithra - Security Audit & Überlegungen

## Versionsverwaltung
- **Version:** 1.0 (Foundation Phase)
- **Status:** Entwurf
- **Zuletzt aktualisiert:** 2026-10-03

---

## 1. Security Philosophy

### 1.1 Grundsätze
- **Security by Design:** Sicherheit ist keine nachträgliche Überlegung, sondern integraler Teil der Architektur
- **Least Privilege:** Minimale Rechte für Komponenten und Benutzer
- **Defense in Depth:** Multiple Security-Layers (Server + Client + Network)
- **Privacy First:** Minimale Datenerhebung, DSGVO-Konformität

### 1.2 Bedrohungsmodell (MVP Phase)
| Bedrohung | Eintrittswahrscheinlichkeit | Impact | Mitigation |
|-----------|----------------------------|--------|------------|
| Code Injection | Low (Local Only) | High | Input Validation, Sandboxing |
| Data Leakage | Medium | Medium | Keine Sensiblen Daten im Code |
| Account Takeover | Low (Phase 1) | High | Auth-Implementation erst Phase 3 |
| Cheating (PvE) | Medium | Medium | Deterministic Engine, Server-Validation (später) |
| UI Exploits | Low | Medium | Input Sanitization, Rate Limiting |

---

## 2. Code Security Guidelines

### 2.1 Input Validation (Kritisch)
Alle Benutzereingaben müssen validiert werden, auch wenn "intern":

```python
# Richtig
def play_card(card_id: str, target_id: str | None = None):
    # Validation vor jeder Nutzung
    assert card_id in valid_cards, f"Ungültige Karte: {card_id}"
    if target_id:
        assert target_id in valid_targets, f"Ungültiges Ziel: {target_id}"
    
    # Sandbox-Check: Karte darf in current Game Phase gespielt werden
    assert game_phase.allow_play(card_type), f"Karte nicht in Phase {game_phase} playable"
    
    # Executie...
```

### 2.2 Keine Secrets im Code
- **Nie** Passwörter, Tokens, Keys im Source Code hardcodieren
- Nutzung von Environment Variables (via `os.getenv()` oder `python-dotenv`)
- `.env` Dateien sind in `.gitignore` (wenn git genutzt wird)

### 2.3 Output Encoding (für UI/Logs)
- UI Output muss encoded werden, um XSS-like Probleme zu vermeiden
- Logs dürfen keine sensiblen Karten-Daten oder User-Infos enthalten

---

## 3. Data Protection

### 3.1 Sensible Daten-Kategorien
| Datenkategorie | Speicherung | Schutzmaßnahme |
|----------------|-------------|----------------|
| Passwörter | Hashing (bcrypt/Argon2) | Never plaintext |
| API Tokens | Encrypted Storage | Environment Variables |
| Zahlungsdaten | Nicht speichern (3rd Party Gateway) | PCI-DSS Konformität |
| Spielstand/Progression | SQLite/Cloud | Verschlüsselung bei Ruhezustand (SQLCipher/Encryption) |
| Telemetrie | Aggregiert, anonimisiert | Opt-Out Option |

### 3.2 DSGVO-Betrachtungen
- **Keine** persönlichen Daten ohne explizite Einwilligung
- **Recht auf Löschung:** User können Account & Daten löschen
- **Dataminimierung:** Nur Daten sammeln, die für Spielbetrieb nötig sind
- **Alterskontrolle:** Mindestalter 13+ (oder PEGI-12)

---

## 4. Network Security (Phase 3+)

### 4.1 Authentifizierung
| Feature | Implementation |
|---------|---------------|
| **Login** | JWT Tokens (short-lived + Refresh Tokens) |
| **Session** | HttpOnly, Secure Cookies + SameSite=Strict |
| **Rate Limiting** | pro IP/User, progressive delays |
| **MFA** | Optional (Phase 4+, SMS/Authenticator App) |

### 4.2 Verschlüsselung
- **TLS 1.3+** für alle Netzwerk-Kommunikation
- **WebSocket** wss:// (nicht ws://)
- **Certificate Pinning** für mobile Clients (optional)

### 4.3 Datenintegrität
- **Signed Packets** für kritische Game State Updates
- **Checksums** für heruntergeladene Card-Daten
- **Replay Validation** für recorded Games (Anti-Cheat)

---

## 5. Client-Side Security (Flet UI)

### 5.1 Sandbox-Beschränkungen
- Flet-Apps laufen im Kontext des Browsers/Desktops
- **Keine** direkten Dateisystem-Zugriff ohne User-Auswahl (File Picker API)
- **Keine** external network calls abseits der API

### 5.2 Common Vulnerabilities (Prüfung)
| Vulnerability | Check |
|---------------|-------|
| **XSS** | Alle UI-Variablen werden encoded ausgegeben? |
| **CSRF** | Keine state-changing GET Requests (POST-only) |
| **Clickjacking** | X-Frame-Options Header (bei Web) |
| **Open Redirect** | Eigene Domain nur bei Weiterleitungen |
| **Code Injection** | `subprocess`, `eval()`, `exec()` vermeiden |

### 5.3 Secure Coding Checkliste (Pro jede Commits)
- [ ] Keine User Inputs blind vertrauen
- [ ] Sensible Daten nicht in Variablen-Namen oder Kommentaren
- [ ] Error Messages geben keine System-Infos preis (Stack Traces an User ausblenden)
- [ ] Logging filtert sensible Daten vor dem Schreiben
- [ ] Dependencies sind aktuell (`pip-audit`, `safety check`)

---

## 6. Dependency Security

### 6.1 Regular Audits
```bash
# Sicherheits-Checks durchführen
pip audit                    # Known vulnerabilities prüfen
safety check                 # Against known vulnerability DB
pip list --outdated --format=columns  # Updates prüfen
```

### 6.2 Critical Dependencies (Flet-Ökosystem)
| Paket | Sicherheitsstatus | Monitoring |
|-------|------------------|------------|
| `flet` | Aktive Maintenance | Weekly check |
| `fastapi` (falls genutzt) | Gut dokumentiert | Weekly check |
| `pytest` | Sehr stabil | Kein direktes Risk |
| `sqlalchemy` (falls DB) | Regelmäßige Updates | Weekly check |

### 6.3 Vulnerability Response
- **Critical:** Sofortiges Patch (within 24h)
- **High:** innerhalb von 1 Woche
- **Medium:** im nächsten Release-Zyklus
- **Low:** Backlog, priorisiert nach Impact

---

## 7. Cheat-Schutz (Game Integrity)

### 7.1 PvE (Singleplayer/Offline)
- **Deterministische Engine:** Server muss nicht autoritativ sein (für MVP)
- **Replay-System:** Aufzeichnungen können Validiert werden
- **Client Trust:** Basis-Level, kein harter Cheat-Schutz nötig für MVP

### 7.2 PvP (Phase 3+)
- **Server-Authoritative State:** Kritische Game State Teile im Server
- **Move Validation:** Jeder Move wird server-seitig geprüft (Legal Moves only)
- **Rate Limiting:** Verhindert Macro/Script Exploits
- **Anti-Exploit Flags:** Bekanntche Exploits werden gebanned

### 7.3 Known Exploits (Prevention)
| Exploit Typ | Prevention |
|-------------|------------|
| **Damage Hacking** | Server validates Damage Numbers |
| **Deck Stacking** | Deck Randomness server-verified (Seed) |
| **Mana Cheating** | Mana Counter ist server-visible oder TTP |
| **Timeout Abuse** | Server enforced Turn Timers |

---

## 8. Incident Response

### 7.1 Security Contact
- **E-Mail:** security@merithra.local (Placeholder, echte Domain später)
- **Response Time:** 24h für Critical, 72h für High
- **Public Channels:** Bug Bounty Program (Phase 4+)

### 7.2 Reporting Format (für externe Reporter)
```markdown
## Merithra Security Report

### Title
[Kurzer Titel des Problems]

### Severity
[Critical / High / Medium / Low]

### Description
[Detaillierte Beschreibung]

### Steps to Reproduce
1. ...
2. ...

### Affected Versions
[Version Numbers]

### Fixed In
[Version mit Fix]

### Reporter
[Optional: Name/Kontakt]
```

---

## 9. Security Checkliste für Sub-Agenten

### Bei jeder Code-Änderung prüfen:
- [ ] Keine Secrets (Passwörter, Tokens) im Code oder Kommentaren
- [ ] Input Validation für alle User-Actions (auch interne)
- [ ] Log Output filtert sensible Daten
- [ ] Error Messages sind user-friendly, keine Stack Traces
- [ ] Dependencies sind aktuell und ohne bekannte Critical-Vulnerabilities
- [ ] Flet UI: keine `page.run_javascript()` mit user input ohne Sanitization
- [ ] Keine harten Pfade zu lokalen Dateien (relativ oder Environment Variables)
- [ ] Datenbank-Queries nutzen Parameterized Queries (kein SQL Injection Risk)
- [ ] **LLM Prompt: Sensible Spielzustands-Daten nicht im Prompt außerhalb berechtigter Sichtbereiche**

### Bei Multiplayer/Network-Änderungen zusätzlich:
- [ ] Authentifizierungs-Check vor state-changing Operations
- [ ] Rate Limiting ist implementiert
- ** WebSocket Verbindungen sind sicher (wss://)**
- [ ] Datenintegrität via Signatures oder Checksums
- [ ] **LLM Requests: Nur lokaler Ollama-Zugriff, keine externen API-Leaks**

### Bei UI-Änderungen zusätzlich:
- [ ] Tooltips und Labels enthalten keine sensiblen Infos
- [ ] Drag & Drop validiert (keine beliebigen Daten an Server senden)
- [ ] Accessibility Labels sind vorhanden, aber keine Security-Lücken öffnend
- [ ] **LLM-Integration: Fallback bei Modell-Fehler, Spiel ohne KI weiterhin spielbar**

### Bei LLM-spezifischen Änderungen zusätzlich:
- [ ] **Prompt-Leakage: System-Prompt und Regeltexte nicht in User-Antworten enthalten**
- [ ] **Geheime Karten/Handkarten niemals im Prompt an LLM senden**
- [ ] **RNG-Werte nicht in Prompt einbeziehen**
- [ ] **Temperatur-Kontrolle: Strategie niedrig (0.2-0.4), Konversation höher (0.6-0.8)**
- [ ] **Response-Length-Begrenzung: 120-220 Tokens für Strategie, 150-250 für Konversation**
- [ ] **Fallback-Strategie: Bei Ollama-Ausfall Spiel ohne KI-Funktionen weiterführen**
- [ ] **Validierung: Jeder LLM-Vorschlag muss durch Regel-Engine validiert werden**

## 10. Offene Security-Fragen

- [ ] **Auth-System wann implementieren?** (Phase 3 geplant, aber MVP benötigt Basic Auth)
- [ ] **Datenverschlüsselung:** SQLite mit SQLCipher nutzen oder AES nach außen?
- [ ] **Bug Bounty Programm:** Internes Team vs. External Programm starten?
- [ ] **Compliance:** DSGVO-DPA frühzeitig beauftragen (für Live-Ops)?
- [ ] **Third-Party Security Audit:** Wann unabhängigen Audit durchführen?

---

*Dokument-Version: 1.0*  
*Status: Foundation Phase*  
*Erstellt: 2026-10-03*