from blackjack_sim.errors import *


class BonusPlan(object):

    def __init__(self, bonus_config):
        self.name = bonus_config['name']
        self.frequency = bonus_config['frequency']
        self.amount = int(bonus_config['amount'])

        self.num_times_played = 0
        self.num_wins = 0
        self.num_losses = 0
        self.net_amount = 0

    def will_play_bonus_bet(self):
        return self.frequency == 'always'

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
    def get_21_3_payout(self, dealer_up_card, player_hand, bonus_bet):
        if len(player_hand.cards) != 2:
            raise GameplayError(f'Incorrect # of cards ({len(player_hand.cards)}) in player hand for 21+3 bonus')

        multiplier = 0
        is_flush = False
        is_trips = False

        all_cards = [dealer_up_card, player_hand.cards[0], player_hand.cards[1]]

        contains_ace = False
        for c in all_cards:
            if c.rank == 'A':
                contains_ace = True

        # Check for straight
        is_straight = self._check_for_straight(all_cards, self.ACE_LOW_RANK_LOOKUP)

        # If an ace exists (player or dealer) and ace low wasn't a straight then try ace high
        if not is_straight and contains_ace:
            is_straight = self._check_for_straight(all_cards, self.ACE_HIGH_RANK_LOOKUP)

        # Check for flush
        if all_cards[0].suit == all_cards[1].suit == all_cards[2].suit:
            is_flush = True

        # Check for trips
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

    def _check_for_straight(self, cards, rank_lookup):

        sorted_cards = sorted(cards, key=lambda c: rank_lookup[c.rank])

        card_1_idx = rank_lookup[sorted_cards[0].rank]
        card_2_idx = rank_lookup[sorted_cards[1].rank]
        card_3_idx = rank_lookup[sorted_cards[2].rank]

        if card_1_idx + 1 == card_2_idx and card_2_idx + 1 == card_3_idx:
            return True
        else:
            return False
