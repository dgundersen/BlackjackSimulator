


class Card(object):

    CARD_SUITS = ['C', 'D', 'H', 'S']
    CARD_RANKS = ['A', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'J', 'Q', 'K']

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f'{self.rank}'

