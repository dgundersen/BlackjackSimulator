import unittest
import time
from blackjack_sim.game_models import *


class TestGameModels(unittest.TestCase):

    def test_shoe_factory(self):
        num_decks = 2
        shoe_factory = ShoeFactory(num_decks)

        shoe = shoe_factory.get_shoe()

        print(' '.join(c.rank for c in shoe))

        assert shoe
        assert len(shoe) == num_decks * len(Card.CARD_RANKS) * len(Card.CARD_SUITS)

    def test_shoe_factory_performance(self):
        num_decks = 6
        num_shoes = 1000

        shoe_factory = ShoeFactory(num_decks)

        start_time = time.perf_counter()

        for s in range(num_shoes):
            shoe = shoe_factory.get_shoe()

        end_time = time.perf_counter()

        total_time = end_time - start_time
        time_per_shoe = total_time / num_shoes

        print(f"Got {num_shoes} shoes of {num_decks} decks in {total_time:0.4f} seconds")
        print(f"Time per shoe: {time_per_shoe:0.4f} s")

if __name__ == '__main__':
    unittest.main()
