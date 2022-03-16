from blackjack_sim.game_models import Card

class GameManager(object):

    @classmethod
    def get_deck(cls):
        cards = []

        for suit in Card.CARD_SUITS:
            for rank in Card.CARD_RANKS:
                cards.append(Card(suit, rank))

        return cards
