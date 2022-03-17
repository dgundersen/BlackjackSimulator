import unittest
from blackjack_sim.simulation import Simulation

class TestSimulation(unittest.TestCase):

    simulation_config = {
        "name": "Unit Tests Simulation",
        "num_decks": 2,
        "num_players": 3,
        "num_sessions": 1,
        "max_session_hands": 100,
        "min_bet": 15,
        "buyin_num_bets": 20
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

    def test_simulation(self):
        sim = Simulation(self.simulation_config, self.strategy_config)

        assert sim
        assert sim.num_decks == 2
        assert sim.num_players == 3
        assert sim.num_sessions == 1
        assert sim.max_session_hands == 100
        assert sim.min_bet == 15
        assert sim.buyin_num_bets == 20


if __name__ == '__main__':
    unittest.main()
