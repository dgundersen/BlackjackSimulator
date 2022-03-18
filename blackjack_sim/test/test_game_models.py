import unittest
from blackjack_sim.game_models import *


class TestGameModels(unittest.TestCase):

    def test_shoe(self):
        num_decks = 2
        shoe = Shoe(num_decks)

        shoe.print_shoe()

        assert shoe
        assert shoe.cards
        assert len(shoe.cards) == num_decks * len(Card.CARD_RANKS) * len(Card.CARD_SUITS)


if __name__ == '__main__':
    unittest.main()
