from enum import Enum
from random import randint
from blackjack_sim.errors import *


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

        # TODO: change this to a dict lookup instead of .index() every time
        return Card.CARD_STRATEGY_RANKS.index(rank)

class Deck(object):

    def __init__(self):
        self.cards = []
        for suit in Card.CARD_SUITS:
            for rank in Card.CARD_RANKS:
                self.cards.append(Card(suit, rank))

class Shoe(object):

    # Inits a shuffled shoe with the given # of decks
    def __init__(self, num_decks):
        self.cards = []
        for i in range(num_decks):
            deck = Deck()
            for card in deck.cards:
                self.cards.append(card)

        self.cards = self.shuffle(self.cards)

    # Fisher-Yates shuffle; implementation taken from here:
    # https://www.geeksforgeeks.org/shuffle-a-given-array-using-fisher-yates-shuffle-algorithm/
    @staticmethod
    def shuffle(arr):
        n = len(arr)
        for i in range(n - 1, 0, -1):
            j = randint(0, i)

            # Swap arr[i] with the element at random index
            arr[i], arr[j] = arr[j], arr[i]

        return arr

    def print_shoe(self):
        print(' '.join(c.rank for c in self.cards))

class BlackjackHandResult(Enum):
    UNDETERMINED = 0,
    LOSS = 1,
    PUSH = 2,
    WIN = 3

class BlackjackHand(object):

    def __init__(self, player_idx, dealer_hand, bet=0):
        self.player_idx = player_idx
        self.cards = []
        self.hard_value = 0         # All hands have a hard value
        self.soft_value = None      # Hands may not have a soft value
        self.contains_ace = False
        self.is_blackjack = False
        self.is_dealer_hand = dealer_hand
        self.result = BlackjackHandResult.UNDETERMINED

        self.bet = bet

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
            raise GameplayError(f'Tried to add card to hand with hard value of {self.hard_value}')

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
            raise GameplayError('Tried to split dealer hand')

        if len(self.cards) != 2:
            raise GameplayError(f'Can\'t split hand with {len(self.cards)} cards')

        if self.cards[0].rank != self.cards[1].rank:
            raise GameplayError('Tried to split hand with unmatched cards')

        new_hand = BlackjackHand(player_idx=self.player_idx, dealer_hand=False)
        new_hand.add_card(self.cards.pop())

        return new_hand

class BlackjackSession(object):

    def __init__(self, idx, num_players, buyin):
        self.session_idx = idx
        self.num_hands_played = 0
        self.num_players = num_players

        self.players = []
        for p in range(self.num_players):
            self.players.append(BlackjackPlayer(idx=p, buyin=buyin))

class BlackjackPlayer(object):

    def __init__(self, idx, buyin=0):
        self.player_idx = idx
        self.buyin = buyin
        self.chip_stack = buyin
        self.num_hands_played = 0
        self.num_wins = 0
        self.num_pushes = 0
        self.num_losses = 0

        self.hands = []  # list of BlackjackHand objects; will be multiple when we split

    def record_hand_result(self, bj_hand):
        self.num_hands_played += 1

        if bj_hand.result == BlackjackHandResult.WIN:
            self.num_wins += 1

            # pay player; 3:2 for blackjack
            self.chip_stack += 1.5 * bj_hand.bet if bj_hand.is_blackjack else bj_hand.bet

        elif bj_hand.result == BlackjackHandResult.PUSH:
            self.num_pushes += 1

        elif bj_hand.result == BlackjackHandResult.LOSS:
            self.num_losses += 1

            # deduct loss
            self.chip_stack -= bj_hand.bet

        elif bj_hand.result == BlackjackHandResult.UNDETERMINED:
            raise GameplayError('Tried to record UNDETERMINED result')
        else:
            raise GameplayError('Tried to record unknown result')

    def get_gameplay_result_str(self, min_bet):
        pct_win = (self.num_wins / self.num_hands_played) * 100 if self.num_hands_played > 0 else 0
        pct_push = (self.num_pushes / self.num_hands_played) * 100 if self.num_hands_played > 0 else 0
        pct_loss = (self.num_losses / self.num_hands_played) * 100 if self.num_hands_played > 0 else 0

        net_change = self.chip_stack - self.buyin
        net_change_per_hand = net_change / self.num_hands_played if self.num_hands_played > 0 else 0
        edge = -((net_change_per_hand / min_bet) * 100) if min_bet > 0 else 0

        return f'Hands={self.num_hands_played}, Wins={self.num_wins} ({round(pct_win, 1)}%), ' \
               f'Pushes={self.num_pushes} ({round(pct_push, 1)}%), Losses={self.num_losses} ({round(pct_loss, 1)}%), ' \
               f'Stack: ${self.chip_stack}, Net Change: ${net_change}, NC Per Hand: ${round(net_change_per_hand, 2)}, ' \
               f'House Edge: {round(edge, 2)}%'



