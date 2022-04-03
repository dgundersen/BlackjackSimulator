from blackjack_sim.errors import *


class BonusPayer(object):

    STRAIGHT_FLUSH_MX = 30
    TRIPLES_MX = 20
    STRAIGHT_MX = 10
    FLUSH_MX = 5

    SUIT_LOOKUP = {
        'C': 0,
        'D': 1,
        'H': 2,
        'S': 3
    }

    ACE_LOW_RANK_LOOKUP = {
        'A': 0,
        '2': 1,
        '3': 2,
        '4': 3,
        '5': 4,
        '6': 5,
        '7': 6,
        '8': 7,
        '9': 8,
        'T': 9,
        'J': 10,
        'Q': 11,
        'K': 12,
    }

    ACE_HIGH_RANK_LOOKUP = {
        '2': 1,
        '3': 2,
        '4': 3,
        '5': 4,
        '6': 5,
        '7': 6,
        '8': 7,
        '9': 8,
        'T': 9,
        'J': 10,
        'Q': 11,
        'K': 12,
        'A': 13
    }

    def __init__(self):
        pass

    """
    Payouts:
        Straight Flush: 30:1
        3 of a Kind:    20:1
        Straight:       10:1
        Flush:           5:1
    """
    def get_21_3_payout(self, dealer_up_card, player_hand):
        multiplier = 0

        if len(player_hand.cards) != 2:
            raise GameplayError(f'Incorrect # of cards ({len(player_hand.cards)}) in player hand for 21+3 bonus')

        all_cards = [dealer_up_card, player_hand.cards[0], player_hand.cards[1]]

        # TODO: If we have an ace, also sort by ace high
        sorted_cards = sorted(all_cards, key=lambda c: self.ACE_LOW_RANK_LOOKUP[c.rank])

        is_straight = False
        is_flush = False
        is_trips = False

        if sorted_cards[0].value() + 1 == sorted_cards[1].value() and sorted_cards[1].value() + 1 == sorted_cards[2].value():
            is_straight = True

        if sorted_cards[0].suit == sorted_cards[1].suit == sorted_cards[2].suit:
            is_flush = True

        if sorted_cards[0].rank == sorted_cards[1].rank == sorted_cards[2].rank:
            is_trips = True

        if is_straight and is_flush:
            multiplier = self.STRAIGHT_FLUSH_MX
        elif is_trips:
            multiplier = self.TRIPLES_MX
        elif is_straight:
            multiplier = self.STRAIGHT_MX
        elif is_flush:
            multiplier = self.FLUSH_MX

        return multiplier * player_hand.bet


