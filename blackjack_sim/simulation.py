import json
import logging
from random import randint
from blackjack_sim.game_models import Card, Deck, BlackjackHand, BlackjackHandResult
from blackjack_sim.utils import Utils


class SimulationManager(object):

    def __init__(self):
        self.log = Utils.get_logger('SimulationManager', logging.INFO)

        # load main config file; contains 1 or more simulations
        sim_config_list = self.load_json_file('blackjack_sim/simulation_config.json')

        self.simulations = []
        for sim_config in sim_config_list:
            # load strategy config
            if 'strategy_config_file' in sim_config and sim_config['strategy_config_file']:
                strategy_config = self.load_json_file(sim_config['strategy_config_file'])

                self.simulations.append(Simulation(len(self.simulations), sim_config, strategy_config))
            else:
                # TODO: throw ex
                self.log.error('ERROR: No strategy config file')

        self.log.info(f'Loaded {len(self.simulations)} simulations')

    @staticmethod
    def load_json_file(file_name_and_path):
        with open(file_name_and_path, 'r') as f:
            json_file = json.load(f)

        return json_file

    def run_simulations(self):
        for sim in self.simulations:
            sim.run()

class Strategy(object):

    def __init__(self, idx, strategy_config):
        self.log = Utils.get_logger(f'Strategy-{idx}', logging.INFO)

        self.hard_totals = {}  # dict; key=total, val=action
        self.soft_hands = {}  # dict; key=hand, val=action
        self.pairs = {}  # dict; key=hand, val=action

        if 'hard_totals' in strategy_config and strategy_config['hard_totals']:
            for key, value in strategy_config['hard_totals'].items():
                if len(value) != 10:
                    self.log.error(f'ERROR: Invalid # of actions in hard_totals for: {key}')
                else:
                    hand_total = int(key)
                    self.hard_totals[hand_total] = value
        else:
            # TODO: throw ex
            self.log.error('ERROR: Missing hard_totals in strategy config')

        if 'soft_hands' in strategy_config and strategy_config['soft_hands']:
            for key, value in strategy_config['soft_hands'].items():
                if len(value) != 10:
                    self.log.error(f'ERROR: Invalid # of actions in soft_hands for: {key}')
                else:
                    self.soft_hands[key] = value
        else:
            # TODO: throw ex
            self.log.error('ERROR: Missing soft_hands in strategy config')

        if 'pairs' in strategy_config and strategy_config['pairs']:
            for key, value in strategy_config['pairs'].items():
                if len(value) != 10:
                    self.log.error(f'ERROR: Invalid # of actions in pairs for: {key}')
                else:
                    self.pairs[key] = value
        else:
            # TODO: throw ex
            self.log.error('ERROR: Missing pairs in strategy config')


class Simulation(object):

    SHOE_CUTOFF = 30  # if there are fewer than this many cards left then we get a new shoe

    def __init__(self, idx, sim_config, strategy_config):
        self.name = sim_config['name']
        self.num_decks = sim_config['num_decks']
        self.num_players = sim_config['num_players']
        self.num_sessions = sim_config['num_sessions']
        self.max_session_hands = sim_config['max_session_hands']
        self.min_bet = sim_config['min_bet']
        self.buyin_num_bets = sim_config['buyin_num_bets']
        self.verbose = True if 'verbose' in sim_config and int(sim_config['verbose']) == 1 else False

        self.strategy = Strategy(idx, strategy_config)

        self.shoe = []
        self.players = []
        self.dealer = None
        self.num_hands = 0

        log_level = logging.DEBUG if self.verbose else logging.INFO

        self.log = Utils.get_logger(f'Simulation-{idx}', log_level)

    # Returns a shuffled shoe with the # of decks specified in the config file
    def get_shoe(self):
        shoe = []
        for i in range(self.num_decks):
            deck = Deck()
            for card in deck.cards:
                shoe.append(card)

        return self.shuffle(shoe)

    # Fisher-Yates shuffle; implementation taken from here:
    # https://www.geeksforgeeks.org/shuffle-a-given-array-using-fisher-yates-shuffle-algorithm/
    @staticmethod
    def shuffle(arr):
        n = len(arr)
        for i in range(n - 1, 0, -1):
            j = randint(0, i + 1)

            # Swap arr[i] with the element at random index
            arr[i], arr[j] = arr[j], arr[i]

        return arr

    def get_next_card(self):
        return self.shoe.pop(0)

    def run(self):
        self.log.info(f'\nRunning: {self.name}')

        # TODO: get from sim config
        for i in range(3):
            self.play_round()

    def log_all_hands(self):
        self.log.debug('')
        self.log_hand(self.dealer, True)
        for player in self.players:
            self.log_hand(player, False)

    def log_hand(self, bj_hand, is_dealer):
        hand_type_str = 'Dealer' if is_dealer else 'Player'
        self.log.debug(f'{hand_type_str}: {bj_hand} - {bj_hand.result}')
        if bj_hand.linked_hand:
            self.log_hand(bj_hand.linked_hand, is_dealer)

    def play_round(self):
        self.num_hands += 1

        self.log.debug(f'Hand #{self.num_hands}')

        # Check if we need a new shoe
        if len(self.shoe) < self.SHOE_CUTOFF:
            self.shoe = self.get_shoe()
            burn_card = self.get_next_card()

            self.log.debug(f'New shoe of {self.num_decks} decks, {len(self.shoe)} cards; burn card: {burn_card}')

        # Reset hands
        self.dealer = BlackjackHand(dealer_hand=True)
        self.players = []
        for p in range(self.num_players):
            self.players.append(BlackjackHand(dealer_hand=False))

        # Deal 2 rounds of cards
        self.deal_round_of_cards()
        self.deal_round_of_cards()

        self.log_all_hands()

        dealer_up_card = self.dealer.cards[0]

        # Pay 3 card bonus

        # Check if dealer has blackjack
        if self.dealer.is_blackjack:
            for player in self.players:
                if player.is_blackjack:
                    player.result = BlackjackHandResult.PUSH
                else:
                    player.result = BlackjackHandResult.LOSS

        else:
            # Play each player's hand
            for player in self.players:
                self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player)

            # Play dealer's hand
            self.play_dealer_hand()

            # Evaluate each player's hand
            for player in self.players:
                self.evaluate_hand_result(player)

        self.log_all_hands()

        # Pay bust bonus


    def deal_round_of_cards(self):
        # Deal to players
        for player in self.players:
            player.add_card(self.get_next_card())

        # Dealer takes card
        self.dealer.add_card(self.get_next_card())

    def play_dealer_hand(self):
        action = self.determine_dealer_action()

        self.log.debug(f'Playing dealer hand {self.dealer}, Action: {action}')

        # stand
        if action == 'S':
            return

        # hit
        elif action == 'H':
            self.dealer.add_card(self.get_next_card())
            self.play_dealer_hand()

    def determine_dealer_action(self):
        if self.dealer.soft_value and self.dealer.soft_value > 17:
            return 'S'
        elif self.dealer.hard_value >= 17:
            return 'S'
        else:
            return 'H'

    def play_player_hand(self, dealer_up_card, player_hand):
        action = self.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        self.log.debug(f'Playing player hand {player_hand}, Action: {action}')

        # stand
        if action == 'S':
            return

        # hit
        elif action == 'H':
            player_hand.add_card(self.get_next_card())

            # Check if we busted
            if player_hand.hard_value > 21:
                player_hand.result = BlackjackHandResult.LOSS

            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)

        # double
        elif action == 'D':
            # TODO: double bet
            player_hand.add_card(self.get_next_card())

        # split
        elif action == 'SP':
            player_hand.split_hand()
            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)
            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand.linked_hand)

    def determine_player_action(self, dealer_up_card, player_hand):
        num_cards = len(player_hand.cards)
        hand_cards = player_hand.get_hand_as_ranks()
        dealer_up_card_idx = Card.get_dealer_up_card_index(dealer_up_card)

        action = None
        # Determine the player's first action for the hand
        if num_cards == 2:
            if player_hand.is_blackjack:
                action = 'S'
            elif hand_cards in self.strategy.soft_hands.keys():
                action = self.strategy.soft_hands[hand_cards][dealer_up_card_idx]
            elif hand_cards in self.strategy.pairs.keys():
                action = self.strategy.pairs[hand_cards][dealer_up_card_idx]
            elif player_hand.hard_value in self.strategy.hard_totals.keys():
                action = self.strategy.hard_totals[player_hand.hard_value][dealer_up_card_idx]

        # Determine the player's action after initially hitting
        # Follow hard totals strategy and either hit or stand
        elif num_cards > 2:
            if player_hand.hard_value in self.strategy.hard_totals.keys():
                action = self.strategy.hard_totals[player_hand.hard_value][dealer_up_card_idx]

                if action == 'D':
                    action = 'H'

        # There will only be 1 card if we just split
        elif num_cards == 1:
            return 'H'

        # Return action of stand if we're at 21 or busted
        if player_hand.hard_value >= 21:
            action = 'S'

        if not action:
            # TODO: throw ex
            self.log.error(f'ERROR: Unable to determine player action for hand: {hand_cards}')

        return action

    def evaluate_hand_result(self, player_hand):
        if player_hand.result == BlackjackHandResult.UNDETERMINED:
            player_hand_value = player_hand.get_ultimate_value()
            dealer_hand_value = self.dealer.get_ultimate_value()

            if self.dealer.hard_value > 21:
                player_hand.result = BlackjackHandResult.WIN
            elif player_hand.is_blackjack:
                player_hand.result = BlackjackHandResult.WIN
            elif player_hand_value > dealer_hand_value:
                player_hand.result = BlackjackHandResult.WIN
            elif player_hand_value == dealer_hand_value:
                player_hand.result = BlackjackHandResult.PUSH
            elif player_hand_value < dealer_hand_value:
                player_hand.result = BlackjackHandResult.LOSS

        if player_hand.linked_hand:
            self.evaluate_hand_result(player_hand.linked_hand)

