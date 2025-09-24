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
    