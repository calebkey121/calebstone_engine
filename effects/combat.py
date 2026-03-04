from .effect import Effect
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from calebstone_engine.game.game_state import GameState
    from calebstone_engine.core import Ally

class HealAllAlliesEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Heal all allies for {self.amount[0]}"

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        current_player = game_state.current_player
        for ally in current_player.army.allies:
            ally.heal(source=source, amount=self.amount[0])
        return game_state

class DamageEnemyHeroEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Deal {self.amount[0]} damage to the enemy hero"

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        opponent = game_state.opposing_player
        opponent.damage_hero(amount=self.amount[0], source=source)
        return game_state

class DamageAllEnemiesEffect(Effect):
    @property
    def effect_text(self) -> str:
        return f"Deal {self.amount[0]} damage to all enemies"

    def execute(self, game_state: 'GameState', source: 'Ally') -> 'GameState':
        opponent = game_state.opposing_player
        for character in opponent.army.get_all():
            character.damage(source=source, amount=self.amount[0])
        return game_state
