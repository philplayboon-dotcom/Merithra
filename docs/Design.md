# Merithra – UI- und Designkonzept

## Designrichtung

Merithra soll weg von einer klassischen Debug-/Toolbox-Oberfläche hin zu einem klaren, atmosphärischen PvE-Kartenkampfbildschirm entwickelt werden: wenige dominante Informationen, gut lesbare Karten und ein separates, strukturiertes Kampflog statt vieler verstreuter Textausgaben.

### Dark Fantasy Tactical

Das Spiel soll modern, ruhig und fokussiert wirken:

- dunkler, leicht bläulicher Hintergrund statt vieler harter Vollflächen
- Karten und Panels mit klaren Ebenen und dezenten Schatten
- eine Akzentfarbe für den aktiven Spielerzug
- Gold oder Bernstein für Ressourcen und wichtige Werte
- Rot nur für Schaden, Gefahr und negative Effekte
- Grün nur für Heilung, positive Effekte und bestätigte Aktionen
- große, gut erkennbare Icons statt erklärender Textwände
- Animationen sparsam einsetzen: Bewegung und Hervorhebung nur bei wichtigen Ereignissen

### Farbpalette

| Verwendung | Farbe |
|---|---|
| Hintergrund | `#0B1020` |
| Panel | `#151C2E` |
| Panel heller | `#202A40` |
| Primärtext | `#F4F7FB` |
| Sekundärtext | `#9AA7BD` |
| Gold/Ressource | `#E7B85C` |
| Spieler-Akzent | `#5CA9FF` |
| Gegner-Akzent | `#E56565` |
| Erfolg/Heilung | `#68C98B` |

## Bildschirmaufteilung

```text
┌────────────────────────────────────────────────────────────┐
│ Gegnerprofil                         Runde 4 · Gegnerzug   │
│ Name · Lebenspunkte · Status                                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│              Gegnerische Karten / Gegnerfeld               │
│                                                            │
│                 Kampfzone / Zielbereich                    │
│                                                            │
│              Eigene Karten / eigenes Spielfeld              │
│                                                            │
├───────────────────────────────┬────────────────────────────┤
│ Eigene Hand                   │ Kampflog / Ereignisse       │
│ Karten mit Kosten und Werten  │ kompakte Meldungen          │
├───────────────────────────────┴────────────────────────────┤
│ Spielerprofil · Ressourcen · Aktionen · Endturn              │
└────────────────────────────────────────────────────────────┘
```

Das Kampflog soll den zentralen Spielfluss nicht dominieren. Es ist eine sekundäre Informationsquelle, die man schnell überfliegen kann.

## Anzeigen

### Lebenspunkte

Lebenspunkte sollen nicht nur als Text wie `HP: 23/30` erscheinen, sondern als Kombination aus:

- großem Zahlenwert
- horizontalem Lebensbalken
- kleinem Maximalwert
- Statussymbolen darunter

Beispiel:

```text
23 / 30
███████████████░░░░░
Vergiftet · 2 Runden
```

Der Balken soll abhängig vom Zustand reagieren:

- über 60 Prozent: grün/blau
- 30–60 Prozent: gold/orange
- unter 30 Prozent: rot

### Ressourcen und Zugstatus

Runde und Ressourcen gehören in eine kompakte Statusleiste:

```text
RUNDE 4                         MANA 6 / 8
                               ● ● ● ● ● ● ○ ○
```

Für Ressourcen eignen sich einzelne Kristalle oder Kreise besser als eine reine Textausgabe. Der Textwert soll für Lesbarkeit und Barrierefreiheit erhalten bleiben.

### Aktiver Zug

Der aktive Spielerzug soll an drei Stellen erkennbar sein:

- farbiger Rahmen um das aktive Profil
- kleine Statusmeldung oben: `DEIN ZUG`
- hervorgehobener Button: `ZUG BEENDEN`

Während des gegnerischen Zuges soll der Button deaktiviert oder durch `GEGNER IST AM ZUG` ersetzt werden.

## Kartenlayout

Karten sind das wichtigste Element der Oberfläche. Sie sollen nach dem Prinzip „wenige Informationen, aber sofort erfassbar“ gestaltet werden.

```text
┌──────────────────┐
│ Kosten       Typ │
│                  │
│      Artwork     │
│                  │
│ Kartenname       │
│ kurze Fähigkeit  │
│                  │
│ ⚔ 4        ❤ 3  │
└──────────────────┘
```

Eine Karte soll enthalten:

- Kartenname immer an derselben Position
- Kosten oben links als farbiger Kreis
- Kartentyp oben rechts als kleines Icon
- Angriff und Leben unten mit festen Symbolen
- Fähigkeitstext maximal drei bis vier Zeilen
- Beschreibung nicht als langer Fließtext
- Tooltip oder Detailansicht für vollständige Kartentexte
- spielbare Karten mit hellem Rand und leichtem Glow
- nicht spielbare Karten abgedunkelt, aber nicht vollständig ausgegraut

### Karteninteraktion

Die Oberfläche soll klar zeigen:

- welche Karte ausgewählt ist
- wohin sie gespielt werden kann
- welches Ziel benötigt wird
- warum eine Aktion nicht möglich ist

Beispiel:

```text
Ziel benötigt: Wähle einen Gegner aus.
```

Das ist besser als eine allgemeine Ausgabe wie `Ungültige Aktion`.

## Kampflog

Das Kampflog soll keine unstrukturierte Liste von Debug-Ausgaben sein. Ereignisse sollen typisiert und visuell unterschieden werden:

```text
Runde 4
────────────────────
⚔ Wächter greift Goblin an       -4
✚ Priester heilt Wächter         +3
◆ Goblin erhält „Verwundbar“
↻ Gegner beendet seinen Zug
```

### Regeln für Textausgaben

- eine Meldung pro Zeile
- wichtigste Information zuerst
- Zahlen rechtsbündig oder farblich hervorgehoben
- maximal etwa sechs sichtbare Einträge
- ältere Meldungen scrollbar oder einklappbar
- technische Informationen nur in einem Debug-Modus
- keine vollständigen Python-Objekte oder internen IDs im normalen UI

Statt:

```text
Entity(id=3, name='Goblin', health=4, effects=[...]) attacked Entity(...)
```

besser:

```text
Goblin greift Wächter an · 4 Schaden
```

Intern kann das Log weiterhin strukturierte Events verwenden:

```python
CombatEvent(
    event_type="attack",
    actor="Goblin",
    target="Wächter",
    value=4,
)
```

Die UI entscheidet dann, wie dieses Event dargestellt wird. Dadurch bleiben Spielengine und Darstellung sauber getrennt.

## Text-Hierarchie

| Verwendung | Empfehlung |
|---|---:|
| Haupttitel | 24–28 px |
| Bereichstitel | 16–18 px |
| Kartenname | 14–16 px |
| Standardtext | 12–14 px |
| Hilfstext | 10–12 px |
| Lebenspunkte/Schaden | 18–24 px |

Die Oberfläche soll nicht ausschließlich über Farbe kommunizieren. Ein negativer Effekt braucht zusätzlich ein Symbol und einen Namen:

```text
☠ Vergiftet · 2
```

## Technische Struktur

Die Darstellung soll stärker in eigenständige Komponenten zerlegt werden:

```text
client/components/
├── card_view.py
├── card_hand.py
├── player_panel.py
├── resource_bar.py
├── combat_log.py
├── turn_banner.py
├── action_bar.py
├── status_effects.py
└── tooltip.py
```

`game_board.py` soll hauptsächlich koordinieren:

```python
class GameBoard:
    def __init__(self, game_state):
        self.player_panel = PlayerPanel(...)
        self.enemy_panel = PlayerPanel(...)
        self.card_hand = CardHand(...)
        self.combat_log = CombatLog(...)
        self.action_bar = ActionBar(...)

    def render(self, surface):
        self.render_background(surface)
        self.enemy_panel.render(surface)
        self.render_battlefield(surface)
        self.card_hand.render(surface)
        self.combat_log.render(surface)
        self.action_bar.render(surface)
```

Das Theme soll keine einzelnen Farben verstreut im Code enthalten. Stattdessen sollen semantische Farben definiert werden:

```python
COLORS = {
    "background": "#0B1020",
    "panel": "#151C2E",
    "panel_hover": "#202A40",
    "text_primary": "#F4F7FB",
    "text_secondary": "#9AA7BD",
    "accent_player": "#5CA9FF",
    "accent_enemy": "#E56565",
    "resource": "#E7B85C",
    "healing": "#68C98B",
    "damage": "#E56565",
}
```

Zusätzlich ist ein kleines Design-System für folgende Bereiche sinnvoll:

- Abstände
- Rundungen
- Rahmenstärken
- Schatten
- Schriftgrößen
- Animationen
- Statusfarben

## Umsetzungsreihenfolge

1. Theme und Layout-Raster überarbeiten: Hintergrund, Panels, Abstände und Schriftfarben.
2. Spieler- und Gegnerprofil neu bauen: Lebenspunkte, Status, Ressourcen und Zugstatus.
3. Kartenansicht verbessern: feste Informationshierarchie sowie Zustände für Hover, Selected, Playable und Disabled.
4. Kampflog durch strukturierte Events ersetzen: verständliche Meldungen, Ereignisfarben und Scrollbereich.
5. Aktionsleiste und Zugstatus ergänzen.
6. Tooltips und Detailansichten hinzufügen.
7. Animationen und Übergänge zuletzt einbauen.

Der größte unmittelbare Gewinn dürfte aus drei Änderungen kommen: neues Layout-Raster, überarbeitete Kartenkomponente und ein strukturiertes Kampflog. Dafür muss die Spiellogik zunächst nicht geändert werden; die bestehende Engine kann dieselben Daten liefern und sie nur moderner darstellen.