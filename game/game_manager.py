from .game_state import GameState
from .game_logic import GameLogic
from calebstone_engine.config import PlayerConfig, GameConfig
from calebstone_engine.output import NoOutputHandler
from calebstone_engine.tracking import SimulationRecord, GameRecordEmitter
from calebstone_engine.controllers import Controller
from typing import Optional
import random, secrets
import threading
import time

class GameManager:
    def __init__(self,
                 game_config: GameConfig = GameConfig(),
                 p1_config: PlayerConfig = PlayerConfig(),
                 p2_config: PlayerConfig = PlayerConfig(),
                 log_file: Optional[str] = None,
                 seed: Optional[int] = None):

        self.seed = int(seed) if seed is not None else secrets.randbits(32)
        self.rng = random.Random(self.seed)
        self.p1 = p1_config
        self.p2 = p2_config
        self.p1_controller = Controller.create_controller(p1_config.controller)
        self.p2_controller = Controller.create_controller(p2_config.controller)
        self.game_state = GameState(
            game_config=game_config,
            p1_config=p1_config,
            p2_config=p2_config,
            rng=self.rng,
        )
        self.game_record = GameRecordEmitter(log_file=log_file)
        self.output_handler = NoOutputHandler() # ActionHistoryFileHandler("game_history.log")

        # Protect game_state reads/writes so concurrent server reads do not observe partial updates.
        self._state_lock = threading.RLock()

        # Synchronous external action submission state.
        # One API thread can submit while run_game/process_turn executes on another thread.
        self._submission_cv = threading.Condition()
        self._pending_submission = None
        self._next_submission_id = 1
        
        self.start_game()

    @staticmethod
    def _normalize_engine_action(action):
        if not isinstance(action, dict):
            return None, "action must be a dict"

        action_type = action.get("type")
        if action_type == "end_turn":
            return {"type": "end_turn"}, None

        if action_type == "play_card":
            card_index = action.get("card_index")
            if not isinstance(card_index, int):
                return None, "play_card requires integer card_index"
            return {"type": "play_card", "card_index": card_index}, None

        if action_type == "attack":
            attacker_index = action.get("attacker_index")
            target_index = action.get("target_index")
            if not isinstance(attacker_index, int) or not isinstance(target_index, int):
                return None, "attack requires integer attacker_index and target_index"
            return {
                "type": "attack",
                "attacker_index": attacker_index,
                "target_index": target_index,
            }, None

        return None, f"unknown action type: {action_type}"

    def _take_pending_submission(self):
        with self._submission_cv:
            pending = self._pending_submission
            if not pending or pending.get("status") != "queued":
                return None
            pending["status"] = "processing"
            self._pending_submission = None
            self._submission_cv.notify_all()
            return pending

    def _complete_submission(self, submission, status: str, error: Optional[str] = None):
        with self._submission_cv:
            submission["status"] = status
            submission["error"] = error
            self._submission_cv.notify_all()

    def _reject_queued_submission_if_any(self, error: str):
        with self._submission_cv:
            pending = self._pending_submission
            if pending and pending.get("status") == "queued":
                self._pending_submission = None
                pending["status"] = "rejected"
                pending["error"] = error
                self._submission_cv.notify_all()

    def _legal_actions_unlocked(self):
        if GameLogic.is_game_over(self.game_state):
            return []
        return self.game_state.possible_actions()

    def get_legal_actions(self) -> list[dict]:
        """
        Thread-safe legal-action view for the current player, in engine/index format.
        Returns [] when the game is over.
        """
        with self._state_lock:
            # return copies so callers cannot mutate internal action objects
            return [dict(action) for action in self._legal_actions_unlocked()]

    def _apply_action(self, action):
        with self._state_lock:
            self.output_handler.display_action(action, self.game_state)
            GameLogic.process_turn(self.game_state, action)
            
            is_turn_complete = (GameLogic.is_game_over(self.game_state) or 
                              action["type"] == "end_turn")
            
            if is_turn_complete and not GameLogic.is_game_over(self.game_state):
                GameLogic.start_turn(self.game_state)
                self.output_handler.display_state(self.game_state)
                
            return is_turn_complete

    def submit_action_and_wait(self, action: dict, timeout: float | None = None) -> bool | dict:
        """
        Submit one engine-format action to the game loop and block until applied/rejected/timeout.

        Returns:
          - True on success
          - {"applied": False, "status": 422, "error": "..."} when rejected/illegal
          - {"applied": False, "status": 504, "error": "..."} on timeout
        """
        normalized_action, parse_error = self._normalize_engine_action(action)
        if parse_error:
            return {"applied": False, "status": 422, "error": parse_error}

        deadline = None
        if timeout is not None:
            timeout = max(0.0, float(timeout))
            deadline = time.monotonic() + timeout

        with self._state_lock:
            is_over = GameLogic.is_game_over(self.game_state)
        if is_over:
            return {"applied": False, "status": 422, "error": "game is over"}

        with self._submission_cv:
            # One in-flight external action at a time.
            while self._pending_submission is not None:
                remaining = None if deadline is None else (deadline - time.monotonic())
                if remaining is not None and remaining <= 0:
                    return {"applied": False, "status": 504, "error": "timed out waiting to submit action"}
                self._submission_cv.wait(timeout=remaining)

            submission = {
                "id": self._next_submission_id,
                "action": normalized_action,
                "status": "queued",      # queued -> processing -> applied/rejected
                "error": None,
            }
            self._next_submission_id += 1
            self._pending_submission = submission
            self._submission_cv.notify_all()

            while submission["status"] in ("queued", "processing"):
                remaining = None if deadline is None else (deadline - time.monotonic())
                if remaining is not None and remaining <= 0:
                    # If still queued and not yet picked up, remove it from the queue.
                    if submission["status"] == "queued" and self._pending_submission is submission:
                        self._pending_submission = None
                        submission["status"] = "timed_out"
                        self._submission_cv.notify_all()
                    return {"applied": False, "status": 504, "error": "timed out waiting for action to apply"}
                self._submission_cv.wait(timeout=remaining)

            if submission["status"] == "applied":
                return True

            # Rejected by legality check or action processing.
            return {
                "applied": False,
                "status": 422,
                "error": submission.get("error") or "action rejected",
            }
    
    def start_game(self):
        """Initialize game state"""
        with self._state_lock:
            GameLogic.start_game(self.game_state)
            self.game_record.start_game(self.game_state)

            # Write a header to the selected output handler
            if hasattr(self.output_handler, 'display_header'):
                self.output_handler.display_header(self.game_state, seed=self.seed)

            # Begin the first turn and record the turn-start state
            GameLogic.start_turn(self.game_state)
            self.output_handler.display_state(self.game_state)
    
    def process_turn(self):
        """Process actions until turn is complete"""
        with self._state_lock:
            is_over = GameLogic.is_game_over(self.game_state)
        if is_over:
            self._reject_queued_submission_if_any("game is over")
            return True

        p1_turn = self.game_state.current_player == self.game_state.p1
        current_controller = self.p1_controller if p1_turn else self.p2_controller

        # Prioritize externally submitted action when present.
        pending_submission = self._take_pending_submission()
        if pending_submission is not None:
            action = pending_submission["action"]
            legal_actions = self.get_legal_actions()
            if action not in legal_actions:
                self._complete_submission(
                    pending_submission,
                    "rejected",
                    "illegal action for current game state",
                )
                return False
            try:
                is_turn_complete = self._apply_action(action)
            except Exception as exc:
                self._complete_submission(
                    pending_submission,
                    "rejected",
                    f"failed to apply action: {exc}",
                )
                return False
            self._complete_submission(pending_submission, "applied")
            return is_turn_complete

        action = current_controller.get_action(self.game_state)
        if action:
            return self._apply_action(action)
        
        return False  # Return if turn is over
    
    def run_game(self):
        """Run game to completion"""
        while not GameLogic.is_game_over(self.game_state):
            self.process_turn() # consider when controller isn't returning anything...
        self.game_record = self.game_record.end_game(self.game_state, p1_id=self.p1.player_id, p2_id=self.p2.player_id, seed=self.seed)

    @staticmethod
    def run_simulation(game_config: GameConfig, p1_config: PlayerConfig, p2_config: PlayerConfig, num_games: int = 1000, log_file: str = "simulation_results.jsonl"):
        """Run multiple games with random controllers"""
        logger = SimulationRecord()
        for _ in range(num_games):
            game = GameManager(game_config, p1_config, p2_config)
            game.run_game()
            logger.record(game.game_record)
        return logger
    
def main():
    a = GameManager()

if __name__ == "__main__":
    main()
