import random
from game_engine.config import *
from game_engine.effects import TimingWindow


class GameLogic():
    # def __init__(self):
    #     # Initialize game-wide signals
    #     self.signals = GameSignals()
    
    @staticmethod
    def process_turn(game_state, action):
        # Here the action is validated and applied to the game state
        current_player = game_state.current_player
        opponent = game_state.opponent_player
        
        # Resolve action depending on its type
        if action['type'] == 'play_card':
            card_index = action['card_index']
            # no real need to check if has enough gold, below will error if they don't, on them to give valid move
            card = current_player._hand[card_index]
            current_player.play_ally(card)
            # (potentially) subscribe effect that would be triggered later
            GameLogic.subscribe_ally_effect(card, game_state)
        
        elif action['type'] == 'attack':
            attacker = current_player.all_characters()[action['attacker_index']]
            target = opponent.all_characters()[action['target_index']]
            attacker.attack(target)
            # potential addl. attack resolution
        
        elif action['type'] == 'end_turn':
            GameLogic.end_turn(game_state)
        
        else:
            raise ValueError("GameLogic does not recognize action")

        return game_state
    
    @staticmethod
    def is_game_over(game_state):
        # Check if either player's health has reached 0
        return game_state.player1.is_dead() or game_state.player2.is_dead()

    @staticmethod
    def start_game(game_state):
        if game_state.total_turns != 0 or game_state.current_player or game_state.opponent_player:
            raise ValueError("Tried starting the game on non turn zero")
        
        # commented to make player 1 always go first, consider making this an environment var for testing
        # if random.choice([True, False]): # Coin Flip
        if True:
            game_state.current_player = game_state.player1
            game_state.opponent_player = game_state.player2
        else:
            game_state.current_player = game_state.player2
            game_state.opponent_player = game_state.player1
        
        first_player = game_state.current_player
        game_state.who_went_first = first_player # useful info
        second_player = game_state.opponent_player
        
        # Give each player starting gold/income
        first_player.gold = GAME_START['FIRST_PLAYER']['GOLD']
        second_player.gold = GAME_START['SECOND_PLAYER']['GOLD']
        first_player.income = GAME_START['FIRST_PLAYER']['INCOME']
        second_player.income = GAME_START['SECOND_PLAYER']['INCOME']

        # Let each player draw cards
        first_player.draw_cards(GAME_START['FIRST_PLAYER']['CARDS_DRAWN'])
        second_player.draw_cards(GAME_START['SECOND_PLAYER']['CARDS_DRAWN'])

        game_state.total_turns += 1
    
    @staticmethod
    def end_turn(game_state):
        # Directly execute end turn effects - no signals needed
        player = game_state.current_player
        for ally in player.army.allies:
            if (ally._effect and 
                ally._effect.timing == TimingWindow.END_OF_TURN):
                ally._effect.execute(game_state, ally)
        if (game_state.current_round % X_ROUNDS) == 0:
            player.income += INCOME_PER_X_ROUNDS
        game_state.switch_turn()
    
    @staticmethod
    def start_turn(game_state):
        player = game_state.current_player
        player.draw_card()
        # Ready up everyone in current player's army (and here)
        player.army.ready_up()
        player.gold += game_state.current_player.income

        # trigger each start of turn effect
        for ally in player.army.allies:
            if (ally.effect and 
                ally.effect.timing == TimingWindow.START_OF_TURN):
                ally.effect.execute(game_state, ally)
    
    @staticmethod
    def subscribe_ally_effect(card, game_state):
        """
        Subscribe card effects to appropriate signals based on timing window.
        
        Args:
            card: The card whose effects need to be subscribed
            game_state: The current game state for effect execution
        """
        # Map timing windows to their corresponding signal names
        TIMING_TO_SIGNAL = {
            TimingWindow.ON_DEATH: "on_death", # str must match attribute of ally
            TimingWindow.ON_ATTACK: "on_attack",
            TimingWindow.ON_HEAL: "on_heal",
            TimingWindow.ON_DAMAGE_DEALT: "on_damage_dealt",
            # Add new timing windows here as needed
            # TimingWindow.NEW_TIMING: "signal_name",
        }
        if not card._effect:
            return

        # Handle immediate effects
        if card._effect.timing == TimingWindow.ON_PLAY:
            card._effect.execute(game_state, card)
            return

        # Handle delayed effects
        if card._effect.timing in TIMING_TO_SIGNAL:
            signal_name = TIMING_TO_SIGNAL[card._effect.timing]
            if hasattr(card, signal_name):
                signal = getattr(card, signal_name)
                signal.connect(lambda source: card._effect.execute(game_state, source))
