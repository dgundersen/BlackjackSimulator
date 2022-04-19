from blackjack_sim.errors import *


class BonusPlan(object):

    CARD_LOOKUP = {
        '2': False,
        '3': False,
        '4': False,
        '5': False,
        '6': False,
        '7': False,
        '8': False,
        '9': False,
        'T': False,
        'J': False,
        'Q': False,
        'K': False,
        'A': False
    }

    def __init__(self, bonus_config):
        self.name = bonus_config['name']
        self.frequency = bonus_config['frequency']
        self.amount = int(bonus_config['amount'])

        self.num_times_played = 0
        self.num_wins = 0
        self.num_losses = 0
        self.net_amount = 0

        if self.frequency == 'low':
            self.CARD_LOOKUP['2'] = True
            self.CARD_LOOKUP['3'] = True
            self.CARD_LOOKUP['4'] = True
            self.CARD_LOOKUP['5'] = True
            self.CARD_LOOKUP['6'] = True
        elif self.frequency == 'low+ace':
            self.CARD_LOOKUP['2'] = True
            self.CARD_LOOKUP['3'] = True
            self.CARD_LOOKUP['4'] = True
            self.CARD_LOOKUP['5'] = True
            self.CARD_LOOKUP['6'] = True
            self.CARD_LOOKUP['A'] = True

    """
        Frequency options:
        21+3: always
        bust: always, low, low+ace
        
        low = 2 - 6
        low+ace = 2 - 6, A
    """
    def will_play_bonus_bet(self, dealer_up_card=None):
        if self.frequency == 'always':
            return True
        elif self.frequency == 'low' and dealer_up_card:
            return self.CARD_LOOKUP[dealer_up_card.rank]
        elif self.frequency == 'low+ace' and dealer_up_card:
            return self.CARD_LOOKUP[dealer_up_card.rank]
        else:
            return False

    def record_bonus_result(self, payout):
        self.num_times_played += 1

        if payout:
            # win
            self.num_wins += 1
            self.net_amount += payout
        else:
            # loss
            self.num_losses += 1
            self.net_amount -= self.amount

    def get_result_str(self):
        pct_win = (self.num_wins / self.num_times_played) * 100 if self.num_times_played > 0 else 0
        pct_loss = (self.num_losses / self.num_times_played) * 100 if self.num_times_played > 0 else 0

        net_change_per_hand = self.net_amount / self.num_times_played if self.num_times_played > 0 else 0
        edge = -((net_change_per_hand / self.amount) * 100) if self.amount > 0 else 0

        return f'{self.name}: Played={self.num_times_played}, Wins={self.num_wins} ({round(pct_win, 1)}%), Losses={self.num_losses} ({round(pct_loss, 1)}%), ' \
               + f'Net: ${self.net_amount}, House Edge: {round(edge, 2)}%'


class BonusPayer(object):

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
        'K': 12
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

    def _is_straight(self, cards, rank_lookup):

        sorted_cards = sorted(cards, key=lambda c: rank_lookup[c.rank])

        card_1_idx = rank_lookup[sorted_cards[0].rank]
        card_2_idx = rank_lookup[sorted_cards[1].rank]
        card_3_idx = rank_lookup[sorted_cards[2].rank]

        if card_1_idx + 1 == card_2_idx and card_2_idx + 1 == card_3_idx:
            return True
        else:
            return False

    def _is_flush(self, cards):
        suits_found = {}
        for card in cards:
            suits_found[card.suit] = 1

        return len(suits_found.keys()) == 1


class TwentyOne3BonusPayer(BonusPayer):
    """
    Payouts:
        Straight Flush: 30:1
        3 of a Kind:    20:1
        Straight:       10:1
        Flush:           5:1
    """
    STRAIGHT_FLUSH_MX = 30
    TRIPLES_MX = 20
    STRAIGHT_MX = 10
    FLUSH_MX = 5

    def get_payout(self, dealer_up_card, player_hand, bonus_bet):
        if len(player_hand.cards) != 2:
            raise GameplayError(f'Incorrect # of cards ({len(player_hand.cards)}) in player hand for 21+3 bonus')

        multiplier = 0

        all_cards = [dealer_up_card, player_hand.cards[0], player_hand.cards[1]]

        contains_ace = False
        for c in all_cards:
            if c.rank == 'A':
                contains_ace = True

        # Check for straight
        is_straight = self._is_straight(all_cards, self.ACE_LOW_RANK_LOOKUP)

        # If an ace exists (player or dealer) and ace low wasn't a straight then try ace high
        if not is_straight and contains_ace:
            is_straight = self._is_straight(all_cards, self.ACE_HIGH_RANK_LOOKUP)

        # Check for flush
        is_flush = self._is_flush(all_cards)

        # Check for trips
        is_trips = False
        if all_cards[0].rank == all_cards[1].rank == all_cards[2].rank:
            is_trips = True

        if is_straight and is_flush:
            multiplier = self.STRAIGHT_FLUSH_MX
        elif is_trips:
            multiplier = self.TRIPLES_MX
        elif is_straight:
            multiplier = self.STRAIGHT_MX
        elif is_flush:
            multiplier = self.FLUSH_MX

        return multiplier * bonus_bet


class BustBonusPayer(BonusPayer):
    """
    Payouts: Non-Suited   Suited
      Ace:   3:1          50:1
        2:   1:1          25:1
        3:   1:1          15:1
        4:   1:1          10:1
        5:   1:1           5:1
        6:   1:1           3:1
        7:   2:1          15:1
        8:   2:1          10:1
        9:   2:1          20:1
       10:   2:1          20:1
      888:  25:1          75:1
    """

    # Keys are value of the dealer up card.
    # 888 is a special case that will be handled separately.
    MX_LOOKUP = {
        "suited": {
            1: 50,
            2: 25,
            3: 15,
            4: 10,
            5: 5,
            6: 3,
            7: 15,
            8: 10,
            9: 20,
            10: 20
        },
        "non-suited": {
            1: 3,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 2,
            8: 2,
            9: 2,
            10: 2
        }
    }

    def get_payout(self, dealer_hand, bonus_bet):
        multiplier = 0

        if dealer_hand.is_dealer_hand and dealer_hand.hard_value > 21:

            is_flush = self._is_flush(dealer_hand.cards)

            if len(dealer_hand.cards) == 3 and dealer_hand.cards[0].value == 8 and dealer_hand.cards[1].value == 8 and dealer_hand.cards[2].value == 8:
                # 888
                multiplier = 75 if is_flush else 25
            else:
                # just check up card
                payout_set = 'suited' if is_flush else 'non-suited'
                multiplier = self.MX_LOOKUP[payout_set][dealer_hand.cards[0].value]

        return multiplier * bonus_bet


