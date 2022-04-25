from enum import Enum
from random import randint
from blackjack_sim.errors import *
from blackjack_sim.bonuses import *


class Card(object):

    """
    Cards in hands are sorted in the order shown in CARD_RANKS when looking up strategy actions.
    Changing the ordering here will likely break the strategy lookup.
    """
    CARD_RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    CARD_SUITS = ['C', 'D', 'H', 'S']

    CARD_STRATEGY_RANK_LOOKUP = {
        '2': 0,
        '3': 1,
        '4': 2,
        '5': 3,
        '6': 4,
        '7': 5,
        '8': 6,
        '9': 7,
        'T': 8,
        'A': 9
    }


    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

        # hard value
        self.value = self._get_value()

        # used to look up strategy action to take based on dealer up card
        self.dealer_up_card_index = self._get_dealer_up_card_index()

    def __str__(self):
        return f'{self.rank}'

    def _get_value(self):
        if self.rank in ['2', '3', '4', '5', '6', '7', '8', '9']:
            return int(self.rank)
        elif self.rank in ['T', 'J', 'Q', 'K']:
            return 10
        else:
            return 1  # A

    def _get_dealer_up_card_index(self):
        rank = self.rank
        if rank in ['K', 'Q', 'J']:
            rank = 'T'

        return self.CARD_STRATEGY_RANK_LOOKUP[rank]

class Deck(object):

    def __init__(self):
        self.cards = []
        for suit in Card.CARD_SUITS:
            for rank in Card.CARD_RANKS:
                self.cards.append(Card(suit, rank))

# Instead of creating all Deck and Card objects every time we need a shoe, this keeps master copies to copy and return.
# Over thousands of hands this makes a significant difference in performance.
class ShoeFactory(object):

    def __init__(self, num_decks):
        self._deck_cards_master = Deck().cards
        self._shoe_cards_master = []
        for i in range(num_decks):
            # Make a copy of the deck
            deck = self._deck_cards_master[:]
            for card in deck:
                self._shoe_cards_master.append(card)

    def get_shoe(self):
        # Return a shuffled copy of the master shoe
        new_shoe = self._shoe_cards_master[:]

        return self.shuffle(new_shoe)

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

class BlackjackHandResult(Enum):
    UNDETERMINED = 0,
    LOSS = 1,
    PUSH = 2,
    WIN = 3

class BlackjackHand(object):

    def __init__(self, player, dealer_hand, bet=0):
        self.player = player
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
            self.hard_value += card.value

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

        new_hand = BlackjackHand(player=self.player, dealer_hand=False)
        new_hand.add_card(self.cards.pop())

        return new_hand

class BlackjackSession(object):

    def __init__(self, idx, num_players, buyin, bonus_config=None):
        self.session_idx = idx
        self.num_hands_played = 0
        self.num_players = num_players

        self.players = []
        for p in range(self.num_players):
            self.players.append(BlackjackPlayer(idx=p, buyin=buyin, bonus_config=bonus_config))

class BlackjackPlayer(object):

    def __init__(self, idx, buyin=0, bonus_config=None):
        self.player_idx = idx
        self.buyin = buyin
        self.chip_stack = buyin
        self.num_hands_played = 0
        self.num_wins = 0
        self.num_pushes = 0
        self.num_losses = 0
        self.allowed_to_split = True

        # Key = # of hands split to, Value = # of occurences
        # Ex.: {3:17} - A hand was split to 3 hands 17 times
        self.num_split_hands_dict = {}

        self.hands = []  # list of BlackjackHand objects; will be multiple when we split

        self.bonus_plan_21_3 = BonusPlan(bonus_config['21_3']) if bonus_config and '21_3' in bonus_config else None
        self.bonus_plan_bust = BonusPlan(bonus_config['bust']) if bonus_config and 'bust' in bonus_config else None


    def reset_hands(self):
        self.hands = []
        self.allowed_to_split = True

    def add_hand(self, bj_hand, split_limit):
        self.hands.append(bj_hand)
        if split_limit and len(self.hands) >= split_limit:
            self.allowed_to_split = False

    def will_play_21_3_bonus(self):
        return True if self.bonus_plan_21_3 and self.bonus_plan_21_3.will_play_bonus_bet() else False

    def will_play_bust_bonus(self, dealer_up_card):
        return True if self.bonus_plan_bust and self.bonus_plan_bust.will_play_bonus_bet(dealer_up_card=dealer_up_card) else False

    def record_21_3_bonus_result(self, payout):
        bet_amt = self.bonus_plan_21_3.get_bet_amount()

        self.bonus_plan_21_3.record_bonus_result(payout=payout, bet_amount=bet_amt)

        if payout:
            # win
            self.chip_stack += payout
        else:
            # loss
            self.chip_stack -= bet_amt

    def record_bust_bonus_result(self, payout, dealer_up_card):
        bet_amt = self.bonus_plan_bust.get_bet_amount(dealer_up_card=dealer_up_card)

        self.bonus_plan_bust.record_bonus_result(payout=payout, bet_amount=bet_amt)

        if payout:
            # win
            self.chip_stack += payout
        else:
            # loss
            self.chip_stack -= bet_amt

    def record_hand_result(self, bj_hand):
        self.num_hands_played += 1

        if len(self.hands) > 1:
            if len(self.hands) not in self.num_split_hands_dict:
                self.num_split_hands_dict[len(self.hands)] = 1
            else:
                self.num_split_hands_dict[len(self.hands)] += 1

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

        results = []

        results.append(f'Player {self.player_idx}')

        results.append(f'Hands={self.num_hands_played}, Wins={self.num_wins} ({round(pct_win, 1)}%), Pushes={self.num_pushes} ({round(pct_push, 1)}%), Losses={self.num_losses} ({round(pct_loss, 1)}%), ')

        results.append(f'Stack: ${self.chip_stack}, Net Change: ${net_change}, NC Per Hand: ${round(net_change_per_hand, 2)}, House Edge: {round(edge, 2)}%')

        sorted_num_split_hands = {k: v for k, v in sorted(self.num_split_hands_dict.items())}

        for num_hands, num_times in sorted_num_split_hands.items():
            this_pct_split = (num_times / self.num_hands_played) * 100

            results.append(f'Split to {num_hands}: {num_times} ({round(this_pct_split, 2)}%)')

        # Bonus results
        if self.bonus_plan_21_3:
            results.append(self.bonus_plan_21_3.get_result_str())

        if self.bonus_plan_bust:
            results.append(self.bonus_plan_bust.get_result_str())

        return '\n'.join(results)

