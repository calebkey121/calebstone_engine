from game_engine.effects import Effect
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_engine.GameState import GameState
    from game_engine.Ally import Ally

class DrawCardsEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Draw {self.amount[0]} card{'s' if self.amount[0] > 1 else ''}"

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        current_player = game_state.current_player
        current_player.draw_cards(self.amount[0])
        return game_state
