import unittest
from blackjack_sim.simulation import Simulation
from blackjack_sim.game_models import Card, BlackjackHand

class TestSimulation(unittest.TestCase):

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
        "hard_totals": {
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
    def test_determine_player_action(self):
        sim = self.get_simulation()

        for p1 in Card.CARD_RANKS:
            for p2 in Card.CARD_RANKS:
                for d in Card.CARD_RANKS:
                    # Suits don't matter here
                    player_hand = BlackjackHand(dealer_hand=False)
                    player_hand.add_card(Card('C', p1))
                    player_hand.add_card(Card('C', p2))

                    action = sim.determine_player_action(dealer_up_card=Card('C', d), player_hand=player_hand)

                    assert action

    # Spot check some card combos with the expected action
    def test_determine_player_action_spot_check(self):
        sim = self.get_simulation()

        # dealer up card, player card 1, player card 2, expected action
        scenarios = [
            ['A', 'A', 'A', 'SP'],
            ['K', '8', '8', 'SP'],
            ['K', 'T', 'Q', 'S'],
            ['4', 'T', 'Q', 'S'],
            ['4', '5', '5', 'D'],
            ['6', '5', '5', 'D'],
            ['9', '5', '5', 'D'],
            ['J', '5', '5', 'H'],
            ['2', '9', '9', 'SP'],
            ['7', '9', '9', 'S'],
            ['9', '9', '9', 'SP'],
            ['3', '8', '5', 'S'],
            ['6', '8', '5', 'S'],
            ['8', '8', '5', 'H'],
            ['2', '6', '5', 'D'],
            ['3', '6', '5', 'D'],
            ['6', '6', '5', 'D'],
            ['8', '6', '5', 'D'],
            ['Q', '6', '5', 'D'],
            ['A', '6', '5', 'D'],
            ['2', 'A', '2', 'H'],
            ['6', '2', 'A', 'D'],
            ['2', '7', 'A', 'D'],
            ['7', '7', 'A', 'S'],
            ['9', '7', 'A', 'H'],
            ['A', 'A', '9', 'S'],
            ['6', 'A', '9', 'S'],
        ]

        for sc in scenarios:
            player_hand = BlackjackHand(dealer_hand=False)
            player_hand.add_card(Card('C', sc[1]))
            player_hand.add_card(Card('C', sc[2]))

            action = sim.determine_player_action(dealer_up_card=Card('C', sc[0]), player_hand=player_hand)

            assert action == sc[3]


    # Verify that we're playing this hand correctly: AA2


if __name__ == '__main__':
    unittest.main()
