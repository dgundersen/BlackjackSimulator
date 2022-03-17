


class Card(object):

    CARD_SUITS = ['C', 'D', 'H', 'S']
    CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f'{self.rank}'

    def value(self):
        if self.rank in ['2', '3', '4', '5', '6', '7', '8', '9']:
            return int(self.rank)
        elif self.rank in ['T', 'J', 'Q', 'K']:
            return 10
        else:
            return 1  # A

class Deck(object):

    def __init__(self):
        self.cards = []
        for suit in Card.CARD_SUITS:
            for rank in Card.CARD_RANKS:
                self.cards.append(Card(suit, rank))

class BlackjackHand(object):

    def __init__(self):
        self.cards = []
        self.hard_value = 0         # All hands have a hard value
        self.soft_value = None      # Hands may not have a soft value
        self.contains_ace = False

    def __str__(self):
        hand_str = ''
        for card in self.cards:
            hand_str += card.__str__()
        return f'{hand_str} H={self.hard_value}, S={self.soft_value}'

    def add_card(self, card):
        self.cards.append(card)
        self.calculate_value()

    def calculate_value(self):
        self.hard_value = 0
        self.soft_value = None

        for card in self.cards:
            self.hard_value += card.value()

            if card.rank == 'A':
                self.contains_ace = True

        # Only 1 ace in a hand can count as 11 and only if that won't make the total greater than 21
        self.soft_value = 10 + self.hard_value if self.contains_ace and self.hard_value <= 11 else None




