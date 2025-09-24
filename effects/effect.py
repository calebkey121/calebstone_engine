from .timing import TimingWindow
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from calebstone_engine.game.game_state import GameState
    from calebstone_engine.core import Ally

class Effect:
    def __init__(self, amount: list[int], timing: TimingWindow):
        self.amount = amount
        self.timing = timing
        self.text = self.generate_text()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Effect):
            return NotImplemented
        return (
            self.amount == other.amount and
            self.timing == other.timing
        )

    def generate_text(self) -> str:
        """Generate effect text based on timing and amounts"""
        return f"{self.timing.flavor_name}: {self.effect_text}"

    @property
    def effect_text(self) -> str:
        """Should be overridden by child classes to provide specific effect text"""
        raise NotImplementedError

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        """Execute the effect on the game state"""
        raise NotImplementedError
