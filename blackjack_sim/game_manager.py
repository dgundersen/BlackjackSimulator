from blackjack_sim.game_models import Card
import json

class GameManager(object):

    def __init__(self):
        # load main config file
        sim_config = self.load_json_file('blackjack_sim/simulation_config.json')
        self.num_decks = sim_config['num_decks']

        # load strategy config
        if 'strategy_config_file' in sim_config and sim_config['strategy_config_file']:
            self.strategy_config = self.load_json_file(sim_config['strategy_config_file'])
        else:
            # TODO: throw ex
            print('ERROR: no strategy config file')

    @classmethod
    def get_deck(cls):
        cards = []

        for suit in Card.CARD_SUITS:
            for rank in Card.CARD_RANKS:
                cards.append(Card(suit, rank))

        return cards

    @staticmethod
    def load_json_file(file_name_and_path):
        import json

        with open(file_name_and_path, 'r') as f:
            json_file = json.load(f)

        return json_file

