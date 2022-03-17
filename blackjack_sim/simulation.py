import json
from random import randint
from blackjack_sim.game_models import Card, Deck, BlackjackHand


class SimulationManager(object):

    def __init__(self):
        # load main config file; contains 1 or more simulations
        sim_config_list = self.load_json_file('blackjack_sim/simulation_config.json')

        self.simulations = []
        for sim_config in sim_config_list:
            # load strategy config
            if 'strategy_config_file' in sim_config and sim_config['strategy_config_file']:
                strategy_config = self.load_json_file(sim_config['strategy_config_file'])

                self.simulations.append(Simulation(sim_config, strategy_config))
            else:
                # TODO: throw ex
                print('ERROR: no strategy config file')

        print(f'Loaded {len(self.simulations)} simulations')

    @staticmethod
    def load_json_file(file_name_and_path):
        with open(file_name_and_path, 'r') as f:
            json_file = json.load(f)

        return json_file

    def run_simulations(self):
        for sim in self.simulations:
            sim.run()

class Simulation(object):

    SHOE_CUTOFF = 30  # if there are fewer than this many cards left then we get a new shoe

    def __init__(self, sim_config, strategy_config):
        self.name = sim_config['name']
        self.num_decks = sim_config['num_decks']
        self.num_players = sim_config['num_players']
        self.num_sessions = sim_config['num_sessions']
        self.max_session_hands = sim_config['max_session_hands']
        self.min_bet = sim_config['min_bet']
        self.buyin_num_bets = sim_config['buyin_num_bets']

        self.strategy_config = strategy_config

        self.shoe = []
        self.players = []
        self.dealer = None

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
        print(f'Running: {self.name}')

        if len(self.shoe) < self.SHOE_CUTOFF:
            self.shoe = self.get_shoe()
            burn_card = self.get_next_card()

            print(f'New shoe of {self.num_decks} decks, {len(self.shoe)} cards; burn card: {burn_card}')

        # Reset hands
        self.dealer = BlackjackHand()
        self.players = []
        for p in range(self.num_players):
            self.players.append(BlackjackHand())

        # Deal 2 rounds of cards
        self.deal_round_of_cards()
        self.deal_round_of_cards()

        print(f'Dealer: {self.dealer}')
        for player in self.players:
            print(f'Player: {player}')

        dealer_up_card = self.dealer.cards[0]

        # Play each player's hand
        for player in self.players:
            pass
            # TODO: get action based on cards and dealer's up card

        # Play dealer's hand

        # Evaluate each player's hand


    def deal_round_of_cards(self):
        # Deal to players
        for player in self.players:
            player.add_card(self.get_next_card())

        # Dealer takes card
        self.dealer.add_card(self.get_next_card())



# TODO: do we need this as a class?
class RoundOfPlay(object):

    def __init__(self):
        pass

