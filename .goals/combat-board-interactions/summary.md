# Combat board interactions — completion summary

## Acceptance criteria

- All cards in the player's hand are shown in the bottom hand area without the previous fixed five-card limit; the row scrolls horizontally when needed.
- Affordable cards are highlighted during the player's active turn. Unaffordable or inactive cards are subdued, and clicking an affordable card plays it and refreshes the hand, mana, and field.
- Attack-ready friendly minions are highlighted. Clicking one selects it; clicking a legal opposing minion or the enemy hero resolves the attack immediately.
- Living Taunt minions constrain targets: only Taunt minions are selectable and the enemy hero cannot be attacked until no living Taunt remains.
- The end-turn control is vertically centered at the right edge of the battlefield and advances the turn.
- Interaction guidance was added to `docs/Design.md`; regression tests cover hand size, card play, attacker selection, target click resolution, Taunt rules, hero attacks, and turn ending.

## Iteration history

- Iteration 1: PASS. The Builder implemented the interaction flow and tests; the Inspector independently verified all criteria. Focused board tests passed (15), and the full suite passed (176).

## Inspector notes

- Browser-based visual inspection was unavailable because no browser client was connected. The Flet web app started and returned HTTP 200; layout and interaction behavior were verified using the control tree, implementation, and regression tests.
- Full repository Ruff checking reports existing repository-wide lint findings; focused error/name checks passed.

## Recommendations

- Perform a manual visual check at desktop and narrow window sizes when a browser client is available, especially the right-edge end-turn button and horizontally scrolling hand.
- Address the pre-existing repository-wide Ruff findings separately.
