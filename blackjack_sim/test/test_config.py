from blackjack_sim.simulation import Simulation
from blackjack_sim.game_models import *


class TestConfig(object):

    PLAYER_BUYIN = 500
    SPLIT_LIMIT = 4

    simulation_config = {
        "name": "Unit Tests Simulation",
        "num_decks": 2,
        "num_players": 3,
        "num_sessions": 1,
        "max_session_hands": 100,
        "min_bet": 15,
        "buyin_num_bets": 20,
        "verbose": 0
    }

    # Unit tests expect this strategy to be used
    strategy_config = {
        "_format": "list of actions for dealer up card of: 2, 3, 4, 5, 6, 7, 8, 9, T, A",
        "_key": "H = hit, S = stand, D = double, SP = split",
        "_source": "https://blackjack-strategy.co/blackjack-strategy-chart/blackjack-strategy-card-downtown-las-vegas/",
        "_notes": "Soft hands include AA for when we can't resplit",
        "hard_totals": {
            "3": ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
            "4": ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
            "5": ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
            "6": ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
            "7": ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
            "8": ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
            "9": ["H", "D", "D", "D", "D", "H", "H", "H", "H", "H"],
            "10": ["D", "D", "D", "D", "D", "D", "D", "D", "H", "H"],
            "11": ["D", "D", "D", "D", "D", "D", "D", "D", "D", "D"],
            "12": ["H", "H", "S", "S", "S", "H", "H", "H", "H", "H"],
            "13": ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
            "14": ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
            "15": ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
            "16": ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
            "17": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            "18": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            "19": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            "20": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"]
        },
        "soft_hands": {
            "AA": ["H", "H", "H", "D", "D", "H", "H", "H", "H", "H"],
            "A2": ["H", "H", "H", "D", "D", "H", "H", "H", "H", "H"],
            "A3": ["H", "H", "H", "D", "D", "H", "H", "H", "H", "H"],
            "A4": ["H", "H", "D", "D", "D", "H", "H", "H", "H", "H"],
            "A5": ["H", "H", "D", "D", "D", "H", "H", "H", "H", "H"],
            "A6": ["H", "D", "D", "D", "D", "H", "H", "H", "H", "H"],
            "A7": ["D", "D", "D", "D", "D", "S", "S", "H", "H", "H"],
            "A8": ["S", "S", "S", "S", "D", "S", "S", "S", "S", "S"],
            "A9": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"]
        },
        "pairs": {
            "22": ["SP", "SP", "SP", "SP", "SP", "SP", "H", "H", "H", "H"],
            "33": ["SP", "SP", "SP", "SP", "SP", "SP", "H", "H", "H", "H"],
            "44": ["D", "D", "D", "SP", "SP", "H", "H", "H", "H", "H"],
            "55": ["D", "D", "D", "D", "D", "D", "D", "D", "H", "H"],
            "66": ["SP", "SP", "SP", "SP", "SP", "H", "H", "H", "H", "H"],
            "77": ["SP", "SP", "SP", "SP", "SP", "SP", "H", "H", "H", "H"],
            "88": ["SP", "SP", "SP", "SP", "SP", "SP", "SP", "SP", "SP", "SP"],
            "99": ["SP", "SP", "SP", "SP", "SP", "S", "SP", "SP", "S", "S"],
            "TT": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            "JJ": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            "QQ": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            "KK": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            "AA": ["SP", "SP", "SP", "SP", "SP", "SP", "SP", "SP", "SP", "SP"]
        }
    }

    @staticmethod
    def get_simulation():
        return Simulation(0, TestConfig.simulation_config, TestConfig.strategy_config)

    @staticmethod
    def get_blackjack_hand(ranks_str, suited=False, is_dealer_hand=False):

        if is_dealer_hand:
            hand = BlackjackHand(player=None, dealer_hand=is_dealer_hand)
        else:
            player = BlackjackPlayer(idx=0, buyin=TestConfig.PLAYER_BUYIN)
            hand = BlackjackHand(player=player, dealer_hand=is_dealer_hand)
            player.add_hand(bj_hand=hand, split_limit=TestConfig.SPLIT_LIMIT)

        suit_idx = 0
        for rank in ranks_str:
            if suited:
                suit = 'C'
            else:
                suit = Card.CARD_SUITS[suit_idx]
                suit_idx += 1
                if suit_idx > 3:
                    suit_idx = 0
            hand.add_card(Card(suit, rank))

        return hand


