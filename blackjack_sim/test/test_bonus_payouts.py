import unittest
from blackjack_sim.game_models import *
from common_test_utils import *
from test_config import TestConfig
from blackjack_sim.bonuses import BonusPayer



class TestBonusPayouts(unittest.TestCase):

    @sub_test([
        dict(player_hand_str='53', dealer_up_card_rank='4')
    ])
    def test_21_3_straight_flush_payout(self, player_hand_str, dealer_up_card_rank):

        bonus_payer = BonusPayer()

        # Suited defaults to clubs
        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str, suited=True)
        player_hand.bet = 25

        print(player_hand)
        print(f'Bet: {player_hand.bet}')

        dealer_up_card = Card('C', 'K')

        payout = bonus_payer.get_21_3_payout(dealer_up_card=dealer_up_card, player_hand=player_hand)

        print(payout)

        assert payout == 750



if __name__ == '__main__':
    unittest.main()
