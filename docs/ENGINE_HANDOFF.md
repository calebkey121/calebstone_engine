# Calebstone Engine Handoff

Last updated: 2026-02-28

## Purpose
This document gives a high-level map of `calebstone_engine/` for a human reader or LLM and tracks current engine TODOs.

## Engine At A Glance
- **Runtime owner:** `GameManager` creates controllers, `GameState`, RNG seed, and drives the game loop.
- **Rules executor:** `GameLogic` validates/applies actions and runs turn transitions.
- **State container:** `GameState` holds both players, current turn pointers, round/turn counters, and action generation.
- **Domain model:** `Player -> Deck + Army + Hand + Resources`; `Army` always includes hero at index `0`.
- **Combat model:** `Character` handles attack/damage/heal/death and emits signals.
- **Card/effect model:** cards are defined in `cards/cards.py`; effect behavior in `effects/*`.
- **Simulation model:** `arena/` and `tracking/` run round robins and aggregate stats.

## Key Folders
- `game/`: `game_manager.py`, `game_logic.py`, `game_state.py`
- `core/`: `player.py`, `army.py`, `hero.py`, `ally.py`, `character.py`, `deck.py`, `signal.py`
- `controllers/`: random/human/heuristic/RL policy wrappers
- `cards/`: card catalog and deck composition generation
- `effects/`: timing windows and executable effect classes
- `arena/`: round-robin tournament runner
- `tracking/`: per-game records and simulation analytics
- `output/`: optional terminal/file/json logging handlers

## Action Model (Engine Format)
- `{"type":"play_card","card_index":<hand index>}`
- `{"type":"attack","attacker_index":<current player army index>,"target_index":<opponent army index>}`
- `{"type":"end_turn"}`

Notes:
- Army index `0` is hero; allies are `1..N`.
- `GameState.possible_actions()` now always includes `end_turn`.

## Turn Lifecycle
1. `GameManager.start_game()` calls `GameLogic.start_game()`.
2. Starting player resources and draws are initialized.
3. First `start_turn()` is run immediately.
4. Each loop step gets one action from current controller and applies it.
5. If action is `end_turn`, `GameLogic.end_turn()` swaps current/opposing player.
6. New current player then gets `start_turn()`.

## High-Impact Issues (Current)
1. **[P0] Broken hero-damage effect path**
   - `DamageEnemyHeroEffect.execute()` calls `opponent.damage_hero(...)`, but `Player` has no `damage_hero` method.
   - File: `calebstone_engine/effects/combat.py`

2. **[P0] Delayed ally effect wiring likely broken**
   - `GameLogic.subscribe_ally_effect()` checks/reads signal names on `card` directly (`hasattr(card, "on_death")`) rather than `card.signals`.
   - Result: delayed triggers like `ON_DEATH`, `ON_ATTACK`, etc. may never connect.
   - File: `calebstone_engine/game/game_logic.py`

3. **[P1] Hard dependency on numpy at controller module import**
   - `controllers/controller.py` imports `numpy` at top-level even for random/human/heuristic games.
   - In environments without numpy, engine import/startup fails before gameplay.
   - File: `calebstone_engine/controllers/controller.py`

4. **[P1] Broken controller package exports**
   - `controllers/__init__.py` exports names that do not exist (`TerminalController`) and misspells `HeuristicControllerB`.
   - File: `calebstone_engine/controllers/__init__.py`

5. **[P1] `TerminalOutputHandler` references legacy/non-existent player APIs**
   - Uses fields/methods like `_name`, `get_hero_status`, `get_army_status`, `get_hand_status` not present on current `Player`.
   - File: `calebstone_engine/output/output_handler.py`

6. **[P1] Test harness drift (legacy paths/signatures)**
   - Several test files import old module paths (e.g., `calebstone_engine.GameState`) and old constructor signatures.
   - Current `tests/` is not a reliable safety net until modernized.
   - File: `calebstone_engine/tests/TestFramework.py` and related test cases

7. **[P1 / integration] Server action field mismatch with API doc**
   - Server translator currently expects `attacker_id`/`target_id`, while docs specify `attacker_instance_id`/`defender_ref`.
   - This is outside the engine folder but directly affects engine action submission reliability.
   - Files: `calebstone_server/app/controllers/game_controller.py`, `docs/api_v1.md`

## TODOs
1. [x] Add first-class synchronous action submission on `GameManager` for server use (`submit_action_and_wait` with queued apply, 422 illegal, 504 timeout).

2. [x] Add thread-safe `GameManager.get_legal_actions()` that returns current-player legal actions in engine/index format and returns `[]` when game is over; keep legality source aligned with submit validation.

3. Fix delayed effect subscription plumbing in `GameLogic.subscribe_ally_effect` to use `card.signals` and validate each timing window mapping.
4. Add a `Player.damage_hero(...)` path or refactor `DamageEnemyHeroEffect` to target `opposing_player.hero` directly.
5. Remove top-level non-essential imports from `controllers/controller.py` (make RL-only deps lazy).
6. Repair `controllers/__init__.py` exports to match actual class names.
7. Update or remove stale `TerminalOutputHandler` paths to align with current `Player` API.
8. Modernize engine tests against current module paths and signatures; add coverage for:
   - delayed trigger effects (`ON_DEATH`, `ON_ATTACK`, `ON_DAMAGE_DEALT`, `ON_HEAL`)
   - synchronous action submission behavior (success, illegal, timeout)
   - thread safety around API action submission
9. Optional cleanup: decide whether to allow voluntary `end_turn` even when other actions exist; document final rule clearly.
