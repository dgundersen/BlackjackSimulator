import logging
from enum import Enum
from blackjack_sim.utils import Utils


class Card(object):

    """
    Cards in hands are sorted in the order shown in CARD_RANKS when looking up strategy actions.
    Changing the ordering here will likely break the strategy lookup.
    """
    CARD_RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    CARD_SUITS = ['C', 'D', 'H', 'S']
    CARD_STRATEGY_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']

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

    @classmethod
    def get_dealer_up_card_index(cls, card):
        rank = card.rank
        if rank in ['K', 'Q', 'J']:
            rank = 'T'

        return Card.CARD_STRATEGY_RANKS.index(rank)

class Deck(object):

    def __init__(self):
        self.cards = []
        for suit in Card.CARD_SUITS:
            for rank in Card.CARD_RANKS:
                self.cards.append(Card(suit, rank))

class BlackjackHandResult(Enum):
    UNDETERMINED = 0,
    LOSS = 1,
    PUSH = 2,
    WIN = 3

class BlackjackHand(object):

    def __init__(self, dealer_hand):
        self.cards = []
        self.hard_value = 0         # All hands have a hard value
        self.soft_value = None      # Hands may not have a soft value
        self.contains_ace = False
        self.is_blackjack = False
        self.is_dealer_hand = dealer_hand
        self.result = BlackjackHandResult.UNDETERMINED

        self.log = Utils.get_logger(f'BlackjackHand', logging.INFO)

        self.bet = 0

        self.linked_hand = None     # Splitting adds a new hand here

    def __str__(self):
        hand_str = ''
        for card in self.cards:
            hand_str += card.__str__()
        return f'{hand_str} ({self.hard_value}/{self.soft_value})'

    def get_hand_as_ranks(self):
        # Sort by the order in CARD_RANKS. This only really matters for looking up soft hands.
        sorted_cards = sorted(self.cards, key=lambda c: Card.CARD_RANKS.index(c.rank))
        hand_str = ''
        for card in sorted_cards:
            hand_str += card.rank
        return hand_str

    def add_card(self, card):
        if self.hard_value >= 21:
            self.log.error(f'ERROR: Tried to add card to hand with hard value of {self.hard_value}')
            # TODO: throw ex

        else:
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

        self.is_blackjack = len(self.cards) == 2 and self.soft_value == 21

    # Returns the better of the soft and hard values
    def get_ultimate_value(self):
        if self.soft_value:
            return max(self.soft_value, self.hard_value)
        else:
            return self.hard_value

    def split_hand(self):
        if self.is_dealer_hand:
            self.log.error('ERROR: Tried to split dealer hand')
            # TODO: throw ex

        if len(self.cards) != 2:
            self.log.error(f'ERROR: Can\'t split hand with {len(self.cards)} cards')
            # TODO: throw ex

        if self.cards[0].rank != self.cards[1].rank:
            self.log.error('ERROR: Tried to split hand with unmatched cards')
            # TODO: throw ex

        self.linked_hand = BlackjackHand(dealer_hand=False)
        self.linked_hand.add_card(self.cards.pop())


