# Goal: Restore combat board interactions

## User Request

Das Design ist viel besser aber der Kampf kann nicht weiter gehen da es keine möglichkeit zur Interaktion gibt. Am unteren Rand sollten die gezogenen Karten angezeigt werden die zum ausspielen bereit sind. Eine Karte wird highlighted wenn genug Mana vorhanden ist. Eine Karte auf dem Spielfeld die angreifen kann wird auch highlighted und der Angriff wird mit einem klick auf die Karte ausgeführt. Karten werden von der Hand ausgespielt in dem man auf sie klickt. Am mittleren, rechten Bildrand ist ein Button um den Zug zu beenden.

Clarification: Der Spieler klickt zuerst einen bereiten eigenen Diener und anschließend ein gültiges gegnerisches Ziel an.

## Refined Goal

Restore an immediately playable combat-board flow: display the player's drawn hand at the bottom, visually distinguish cards affordable with current mana, and play an affordable card with a single click. Clearly highlight friendly minions that can attack; clicking one selects it, and clicking a legal enemy minion or the enemy hero executes the attack immediately, while respecting taunt. Place the end-turn control at the board's middle-right edge so the player can reliably advance combat.

## Acceptance Criteria

- [ ] Every card currently in the player's hand is visibly represented in a bottom hand area; no hand cards are silently omitted due to a fixed five-card UI cap.
- [ ] Cards affordable during the player's main phase are visibly highlighted, unaffordable or inactive cards are visibly subdued, and clicking an affordable card plays it and refreshes hand, mana, and board.
- [ ] Friendly minions able to attack are highlighted; clicking one selects it, and clicking a legal enemy minion executes combat immediately without requiring a separate attack-button click.
- [ ] When no living enemy Taunt minion exists, clicking the enemy hero after selecting an attacker executes the hero attack; with living Taunt, only Taunt minions are valid targets and hero attacks are blocked.
- [ ] The end-turn button remains available at the middle-right edge of the combat board and advances the turn.
- [ ] Relevant regression tests pass, and the UI interaction guidance is updated in `docs/Design.md`.

## Scope Boundaries

**In scope:**
- Hand display, affordability and attack highlights, click-to-play, click-to-select-and-attack, clickable enemy hero targeting, and placement of the end-turn action.
- Focused regression coverage and documentation of the interactions.

**Out of scope:**
- A general visual redesign, new card effects or targeting rules, changes to matchmaking/profile flows, and removing optional drag-and-drop support.

## Applicable Project Conventions

**Quality gate command:**
- `pytest -q` (documented project validation); use the focused board tests first.
- `ruff check .` is documented in `docs/TESTING.md`, but no repository-level test/lint task manifest is configured.

**Commit convention:**
- Conventional Commits, `<type>: <subject>`, per `docs/CONTRIBUTING.md`.
- Include role marker for goal iterations and both required trailers: the role-specific `Assisted-by:` trailer and `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

**Guidelines:**
- `docs/Design.md`
- `docs/TESTING.md`
- `docs/CONTRIBUTING.md`

**Rules:**
- No `AGENTS.md`, `CONSTITUTION.md`, or `.agents/guidelines` / `.github/guidelines` were found.
