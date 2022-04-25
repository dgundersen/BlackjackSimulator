import unittest
from blackjack_sim.game_models import *
from common_test_utils import *
from test_config import TestConfig
from blackjack_sim.bonuses import BonusPayer


class TestBonusPayouts(unittest.TestCase):

    @sub_test([
        dict(player_hand_str='53', dealer_up_card_rank='4'),
        dict(player_hand_str='23', dealer_up_card_rank='4'),
        dict(player_hand_str='2A', dealer_up_card_rank='3'),
        dict(player_hand_str='QK', dealer_up_card_rank='A'),
        dict(player_hand_str='QA', dealer_up_card_rank='K'),
        dict(player_hand_str='9J', dealer_up_card_rank='T'),
        dict(player_hand_str='TJ', dealer_up_card_rank='Q'),
        dict(player_hand_str='KQ', dealer_up_card_rank='J'),
    ])
    def test_21_3_straight_flush_payout(self, player_hand_str, dealer_up_card_rank):
        bonus_payer = TwentyOne3BonusPayer()

        # Suited defaults to clubs
        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str, suited=True)

        bonus_bet = 25

        dealer_up_card = Card('C', dealer_up_card_rank)

        payout = bonus_payer.get_payout(dealer_up_card=dealer_up_card, player_hand=player_hand, bonus_bet=bonus_bet)

        assert payout == bonus_bet * bonus_payer.STRAIGHT_FLUSH_MX

    @sub_test([
        dict(player_hand_str='53', dealer_up_card_rank='4'),
        dict(player_hand_str='23', dealer_up_card_rank='4'),
        dict(player_hand_str='2A', dealer_up_card_rank='3'),
        dict(player_hand_str='QK', dealer_up_card_rank='A'),
        dict(player_hand_str='QA', dealer_up_card_rank='K'),
        dict(player_hand_str='9J', dealer_up_card_rank='T'),
        dict(player_hand_str='TJ', dealer_up_card_rank='Q'),
        dict(player_hand_str='KQ', dealer_up_card_rank='J'),
    ])
    def test_21_3_straight_payout(self, player_hand_str, dealer_up_card_rank):
        bonus_payer = TwentyOne3BonusPayer()

        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str, suited=False)

        bonus_bet = 25

        dealer_up_card = Card('C', dealer_up_card_rank)

        payout = bonus_payer.get_payout(dealer_up_card=dealer_up_card, player_hand=player_hand, bonus_bet=bonus_bet)

        assert payout == bonus_bet * bonus_payer.STRAIGHT_MX

    @sub_test([
        dict(player_hand_str='59', dealer_up_card_rank='4'),
        dict(player_hand_str='A9', dealer_up_card_rank='4'),
        dict(player_hand_str='TT', dealer_up_card_rank='4'),
        dict(player_hand_str='TT', dealer_up_card_rank='J'),
        dict(player_hand_str='TJ', dealer_up_card_rank='J')
    ])
    def test_21_3_flush_payout(self, player_hand_str, dealer_up_card_rank):
        bonus_payer = TwentyOne3BonusPayer()

        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str, suited=True)

        bonus_bet = 25

        dealer_up_card = Card('C', dealer_up_card_rank)

        payout = bonus_payer.get_payout(dealer_up_card=dealer_up_card, player_hand=player_hand, bonus_bet=bonus_bet)

        assert payout == bonus_bet * bonus_payer.FLUSH_MX

    @sub_test([
        dict(player_hand_str='55', dealer_up_card_rank='5'),
        dict(player_hand_str='TT', dealer_up_card_rank='T'),
        dict(player_hand_str='KK', dealer_up_card_rank='K'),
        dict(player_hand_str='AA', dealer_up_card_rank='A')
    ])
    def test_21_3_triples_payout(self, player_hand_str, dealer_up_card_rank):
        bonus_payer = TwentyOne3BonusPayer()

        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str, suited=True)

        bonus_bet = 25

        dealer_up_card = Card('C', dealer_up_card_rank)

        payout = bonus_payer.get_payout(dealer_up_card=dealer_up_card, player_hand=player_hand, bonus_bet=bonus_bet)

        assert payout == bonus_bet * bonus_payer.TRIPLES_MX

    # None of these hands should have a payout
    @sub_test([
        dict(player_hand_str='23', dealer_up_card_rank='5'),
        dict(player_hand_str='TT', dealer_up_card_rank='Q'),
        dict(player_hand_str='KQ', dealer_up_card_rank='K'),
        dict(player_hand_str='A2', dealer_up_card_rank='A'),
        dict(player_hand_str='35', dealer_up_card_rank='7')
    ])
    def test_21_3_no_payout(self, player_hand_str, dealer_up_card_rank):
        bonus_payer = TwentyOne3BonusPayer()

        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str, suited=False)

        bonus_bet = 25

        dealer_up_card = Card('C', dealer_up_card_rank)

        payout = bonus_payer.get_payout(dealer_up_card=dealer_up_card, player_hand=player_hand, bonus_bet=bonus_bet)

        assert not payout

    # First card in the hand str is the dealer up card
    @sub_test([
        dict(hand_str='A57T', suited=False, expected_mx=3),
        dict(hand_str='A57T', suited=True, expected_mx=50),
        dict(hand_str='3K9', suited=False, expected_mx=1),
        dict(hand_str='3K9', suited=True, expected_mx=15),
        dict(hand_str='6K8', suited=False, expected_mx=1),
        dict(hand_str='6K8', suited=True, expected_mx=3),
        dict(hand_str='76J', suited=False, expected_mx=2),
        dict(hand_str='76J', suited=True, expected_mx=15),
        dict(hand_str='96Q', suited=False, expected_mx=2),
        dict(hand_str='96Q', suited=True, expected_mx=20),
        dict(hand_str='888', suited=False, expected_mx=25),
        dict(hand_str='888', suited=True, expected_mx=75)
    ])
    def test_bust_bonus_payout(self, hand_str, suited, expected_mx):
        bonus_payer = BustBonusPayer()

        dealer_hand = TestConfig.get_blackjack_hand(ranks_str=hand_str, suited=suited, is_dealer_hand=True)

        bonus_bet = 25

        payout = bonus_payer.get_payout(dealer_hand=dealer_hand, bonus_bet=bonus_bet)

        assert payout == bonus_bet * expected_mx



if __name__ == '__main__':
    unittest.main()
