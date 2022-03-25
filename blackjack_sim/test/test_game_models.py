import unittest
import time
from blackjack_sim.game_models import *


class TestGameModels(unittest.TestCase):

    def test_shoe(self):
        num_decks = 2
        shoe = Shoe(num_decks)

        shoe.print_shoe()

        assert shoe
        assert shoe.cards
        assert len(shoe.cards) == num_decks * len(Card.CARD_RANKS) * len(Card.CARD_SUITS)


    def test_shoe_init_performance(self):
        num_decks = 6
        num_shoes = 1000

        start_time = time.perf_counter()

        for s in range(num_shoes):
            shoe = Shoe(8)

        end_time = time.perf_counter()

        total_time = end_time - start_time
        time_per_shoe = total_time / num_shoes

        print(f"Got {num_shoes} shoes of {num_decks} decks in {total_time:0.4f} seconds")
        print(f"Time per shoe: {time_per_shoe:0.4f} s")


if __name__ == '__main__':
    unittest.main()
