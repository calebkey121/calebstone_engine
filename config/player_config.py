from dataclasses import dataclass
from calebstone_engine.cards import create_deck, DeckType
from calebstone_engine.controllers import Controller

ALLOWED_CONTROLLERS = {"human", "random", "heuristica"}
ALLOWED_DECKS = {
    "standard": lambda: create_deck(DeckType.STANDARD),
    "test": lambda: create_deck(DeckType.TEST),
}

@dataclass(frozen=True)
class PlayerConfig:
    player_id: str
    controller: str
    hero: str
    deck: str

    def __post_init__(self):
        #if self.controller not in ALLOWED_CONTROLLERS:
        #    raise ValueError(f"Unknown controller: {self.controller!r}. Must be one of {ALLOWED_CONTROLLERS}")
        if self.deck not in ALLOWED_DECKS:
            raise ValueError(f"Unknown deck: {self.deck!r}. Must be one of {list(ALLOWED_DECKS.keys())}")

    def build_deck(self):
        return ALLOWED_DECKS[self.deck]()
    
    def get_controller(self):
        return Controller.create_controller(self.controller)
