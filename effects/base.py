from enum import Enum

class TimingWindow(Enum):
    ON_PLAY = "on_play"
    ON_DEATH = "on_death"
    END_OF_TURN = "end_of_turn"
    START_OF_TURN = "start_of_turn"
    ON_ATTACK = "on_attack"
    ON_DAMAGE_DEALT = "on_damage_dealt"
    ON_DAMAGE_TAKEN = "on_damage_taken"
    AFTER_ATTACK = "after_attack"
    ON_HEAL = "on_heal"
    ALWAYS = "always"

    @property
    def flavor_name(self):
        return {
            TimingWindow.ON_PLAY: "Battlecry",
            TimingWindow.ON_DEATH: "Toll of the Dead",
            TimingWindow.END_OF_TURN: "At end of turn",
            TimingWindow.START_OF_TURN: "At start of turn",
            TimingWindow.ON_ATTACK: "When attacking",
            TimingWindow.ON_DAMAGE_DEALT: "After dealing damage",
            TimingWindow.ON_DAMAGE_TAKEN: "After taking damage",
            TimingWindow.AFTER_ATTACK: "After attacking",
            TimingWindow.ON_HEAL: "After being healed",
            TimingWindow.ALWAYS: "Presence"
        }[self]

class Effect:
    def __init__(self, amount: list[int], timing: TimingWindow):
        self.amount = amount
        self.timing = timing
        self.text = self.generate_text()

    def __eq__(self, other: 'Effect') -> bool:
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
