from game_engine.effects import Effect
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_engine.GameState import GameState
    from game_engine.Ally import Ally

class GainGoldEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Gain {self.amount[0]} gold"

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        current_player = game_state.current_player
        current_player.gold += self.amount[0]
        return game_state

class StealGoldEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Steal {self.amount[0]} gold"

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        current_player = game_state.current_player
        actual_amount = min(self.amount[0], game_state.opponent_player.gold)
        game_state.opponent_player.gold -= actual_amount
        game_state.current_player.gold += actual_amount
        return game_state

class StealIncomeEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Steal {self.amount[0]} income"
    
    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        current_player = game_state.current_player
        actual_amount = min(self.amount[0], game_state.opponent_player.income)
        game_state.opponent_player.income -= actual_amount
        game_state.current_player.income += actual_amount
        return game_state

class GainIncomeEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Gain {self.amount[0]} income"

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        current_player = game_state.current_player
        current_player.income += self.amount[0]
        return game_state
