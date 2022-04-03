import unittest
from blackjack_sim.simulation import Simulation
from blackjack_sim.game_models import *
from common_test_utils import *


class TestSimulation(unittest.TestCase):
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

    def get_simulation(self):
        return Simulation(0, self.simulation_config, self.strategy_config)

    def get_blackjack_hand(self, ranks_str, suited=False, is_dealer_hand=False):

        if is_dealer_hand:
            hand = BlackjackHand(player=None, dealer_hand=is_dealer_hand)
        else:
            player = BlackjackPlayer(idx=0, buyin=self.PLAYER_BUYIN)
            hand = BlackjackHand(player=player, dealer_hand=is_dealer_hand)
            player.add_hand(bj_hand=hand, split_limit=self.SPLIT_LIMIT)

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

    def test_simulation(self):
        sim = self.get_simulation()

        assert sim
        assert sim.num_decks == 2
        assert sim.num_players == 3
        assert sim.num_sessions == 1
        assert sim.max_session_hands == 100
        assert sim.min_bet == 15
        assert sim.buyin_num_bets == 20

    # Verify that an action is determined for every possible combination of player hand and dealer up card
    def test_determine_player_action_all_starting_hands(self):
        sim = self.get_simulation()

        for p1 in Card.CARD_RANKS:
            for p2 in Card.CARD_RANKS:
                for d in Card.CARD_RANKS:
                    # Suits don't matter here
                    player_hand = BlackjackHand(player=BlackjackPlayer(idx=0, buyin=500), dealer_hand=False)
                    player_hand.add_card(Card('C', p1))
                    player_hand.add_card(Card('C', p2))

                    action = sim.strategy.determine_player_action(dealer_up_card=Card('C', d), player_hand=player_hand)

                    assert action

    @sub_test([
        dict(player_hand_str='AA', dealer_up_card_rank='A', expected_action='SP'),
        dict(player_hand_str='88', dealer_up_card_rank='K', expected_action='SP'),
        dict(player_hand_str='TQ', dealer_up_card_rank='K', expected_action='S'),
        dict(player_hand_str='TQ', dealer_up_card_rank='4', expected_action='S'),
        dict(player_hand_str='55', dealer_up_card_rank='4', expected_action='D'),
        dict(player_hand_str='55', dealer_up_card_rank='6', expected_action='D'),
        dict(player_hand_str='55', dealer_up_card_rank='9', expected_action='D'),
        dict(player_hand_str='55', dealer_up_card_rank='J', expected_action='H'),
        dict(player_hand_str='99', dealer_up_card_rank='2', expected_action='SP'),
        dict(player_hand_str='99', dealer_up_card_rank='7', expected_action='S'),
        dict(player_hand_str='99', dealer_up_card_rank='9', expected_action='SP'),
        dict(player_hand_str='85', dealer_up_card_rank='3', expected_action='S'),
        dict(player_hand_str='85', dealer_up_card_rank='6', expected_action='S'),
        dict(player_hand_str='85', dealer_up_card_rank='8', expected_action='H'),
        dict(player_hand_str='65', dealer_up_card_rank='2', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='3', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='6', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='8', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='Q', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='A', expected_action='D'),
        dict(player_hand_str='A2', dealer_up_card_rank='2', expected_action='H'),
        dict(player_hand_str='2A', dealer_up_card_rank='6', expected_action='D'),
        dict(player_hand_str='7A', dealer_up_card_rank='2', expected_action='D'),
        dict(player_hand_str='7A', dealer_up_card_rank='7', expected_action='S'),
        dict(player_hand_str='7A', dealer_up_card_rank='9', expected_action='H'),
        dict(player_hand_str='A9', dealer_up_card_rank='A', expected_action='S'),
        dict(player_hand_str='A9', dealer_up_card_rank='6', expected_action='S')
    ])
    # Check some scenarios for the player action determined
    def test_determine_player_action(self, player_hand_str, dealer_up_card_rank, expected_action):
        sim = self.get_simulation()

        player_hand = self.get_blackjack_hand(ranks_str=player_hand_str)
        dealer_up_card = Card('C', dealer_up_card_rank)

        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == expected_action

    # Verify that we're playing these trickier hands correctly
    @sub_test([
        dict(player_hand_str='A2A'),
        dict(player_hand_str='2AA'),
        dict(player_hand_str='A3A'),
        dict(player_hand_str='AAA')
    ])
    def test_high_soft_totals(self, player_hand_str):
        sim = self.get_simulation()

        player_hand = self.get_blackjack_hand(ranks_str=player_hand_str)

        print(f'Player Hand: {player_hand}')

        dealer_up_card = Card('C', 'K')

        # A2A - Hit
        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == 'H'

        player_hand.add_card(Card('C', '2'))

        # A2A2 - Hit
        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == 'H'

        player_hand.add_card(Card('D', '4'))

        # A2A24 (10/20) - Stand
        # AAA24 (9/19) - Stand
        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == 'S'

    # Specifically tests resplitting aces
    def test_resplitting_aces(self):
        sim = self.get_simulation()

        hand_1 = self.get_blackjack_hand(ranks_str='AA')

        player = hand_1.player

        dealer_up_card = Card('C', 'K')

        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_1) == 'SP'

        # First split; now 2 hands
        hand_2 = hand_1.split_hand()
        player.add_hand(bj_hand=hand_2, split_limit=self.SPLIT_LIMIT)

        assert hand_2 is not None

        hand_1.add_card(Card('C', 'A'))
        hand_2.add_card(Card('D', 'A'))

        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_1) == 'SP'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_2) == 'SP'

        # Second split; now 3 hands
        hand_3 = hand_1.split_hand()
        player.add_hand(bj_hand=hand_3, split_limit=self.SPLIT_LIMIT)

        assert hand_3 is not None

        hand_1.add_card(Card('H', 'A'))
        hand_3.add_card(Card('S', 'A'))

        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_3) == 'SP'

        # Third split; now 4 hands; no more splits allowed
        hand_4 = hand_2.split_hand()
        player.add_hand(bj_hand=hand_4, split_limit=self.SPLIT_LIMIT)

        assert hand_4 is not None
        assert player.allowed_to_split is False

        hand_2.add_card(Card('D', 'A'))
        hand_4.add_card(Card('C', 'A'))

        # No more splits allowed so the action for all hands should be Hit
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_1) == 'H'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_2) == 'H'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_3) == 'H'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_4) == 'H'



if __name__ == '__main__':
    unittest.main()
