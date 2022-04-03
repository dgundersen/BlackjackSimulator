import unittest
from blackjack_sim.game_models import *
from common_test_utils import *
from test_config import TestConfig


class TestSimulation(unittest.TestCase):

    def test_simulation(self):
        sim = TestConfig.get_simulation()

        assert sim
        assert sim.num_decks == 2
        assert sim.num_players == 3
        assert sim.num_sessions == 1
        assert sim.max_session_hands == 100
        assert sim.min_bet == 15
        assert sim.buyin_num_bets == 20

    # Verify that an action is determined for every possible combination of player hand and dealer up card
    def test_determine_player_action_all_starting_hands(self):
        sim = TestConfig.get_simulation()

        for p1 in Card.CARD_RANKS:
            for p2 in Card.CARD_RANKS:
                for d in Card.CARD_RANKS:
                    # Suits don't matter here
                    player_hand = BlackjackHand(player=BlackjackPlayer(idx=0, buyin=500), dealer_hand=False)
                    player_hand.add_card(Card('C', p1))
                    player_hand.add_card(Card('C', p2))

                    action = sim.strategy.determine_player_action(dealer_up_card=Card('C', d), player_hand=player_hand)

                    assert action

    @sub_test([
        dict(player_hand_str='AA', dealer_up_card_rank='A', expected_action='SP'),
        dict(player_hand_str='88', dealer_up_card_rank='K', expected_action='SP'),
        dict(player_hand_str='TQ', dealer_up_card_rank='K', expected_action='S'),
        dict(player_hand_str='TQ', dealer_up_card_rank='4', expected_action='S'),
        dict(player_hand_str='55', dealer_up_card_rank='4', expected_action='D'),
        dict(player_hand_str='55', dealer_up_card_rank='6', expected_action='D'),
        dict(player_hand_str='55', dealer_up_card_rank='9', expected_action='D'),
        dict(player_hand_str='55', dealer_up_card_rank='J', expected_action='H'),
        dict(player_hand_str='99', dealer_up_card_rank='2', expected_action='SP'),
        dict(player_hand_str='99', dealer_up_card_rank='7', expected_action='S'),
        dict(player_hand_str='99', dealer_up_card_rank='9', expected_action='SP'),
        dict(player_hand_str='85', dealer_up_card_rank='3', expected_action='S'),
        dict(player_hand_str='85', dealer_up_card_rank='6', expected_action='S'),
        dict(player_hand_str='85', dealer_up_card_rank='8', expected_action='H'),
        dict(player_hand_str='65', dealer_up_card_rank='2', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='3', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='6', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='8', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='Q', expected_action='D'),
        dict(player_hand_str='65', dealer_up_card_rank='A', expected_action='D'),
        dict(player_hand_str='A2', dealer_up_card_rank='2', expected_action='H'),
        dict(player_hand_str='2A', dealer_up_card_rank='6', expected_action='D'),
        dict(player_hand_str='7A', dealer_up_card_rank='2', expected_action='D'),
        dict(player_hand_str='7A', dealer_up_card_rank='7', expected_action='S'),
        dict(player_hand_str='7A', dealer_up_card_rank='9', expected_action='H'),
        dict(player_hand_str='A9', dealer_up_card_rank='A', expected_action='S'),
        dict(player_hand_str='A9', dealer_up_card_rank='6', expected_action='S')
    ])
    # Check some scenarios for the player action determined
    def test_determine_player_action(self, player_hand_str, dealer_up_card_rank, expected_action):
        sim = TestConfig.get_simulation()

        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str)
        dealer_up_card = Card('C', dealer_up_card_rank)

        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == expected_action

    # Verify that we're playing these trickier hands correctly
    @sub_test([
        dict(player_hand_str='A2A'),
        dict(player_hand_str='2AA'),
        dict(player_hand_str='A3A'),
        dict(player_hand_str='AAA')
    ])
    def test_high_soft_totals(self, player_hand_str):
        sim = TestConfig.get_simulation()

        player_hand = TestConfig.get_blackjack_hand(ranks_str=player_hand_str)

        print(f'Player Hand: {player_hand}')

        dealer_up_card = Card('C', 'K')

        # A2A - Hit
        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == 'H'

        player_hand.add_card(Card('C', '2'))

        # A2A2 - Hit
        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == 'H'

        player_hand.add_card(Card('D', '4'))

        # A2A24 (10/20) - Stand
        # AAA24 (9/19) - Stand
        action = sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        assert action == 'S'

    # Specifically tests resplitting aces
    def test_resplitting_aces(self):
        sim = TestConfig.get_simulation()

        hand_1 = TestConfig.get_blackjack_hand(ranks_str='AA')

        player = hand_1.player

        dealer_up_card = Card('C', 'K')

        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_1) == 'SP'

        # First split; now 2 hands
        hand_2 = hand_1.split_hand()
        player.add_hand(bj_hand=hand_2, split_limit=TestConfig.SPLIT_LIMIT)

        assert hand_2 is not None

        hand_1.add_card(Card('C', 'A'))
        hand_2.add_card(Card('D', 'A'))

        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_1) == 'SP'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_2) == 'SP'

        # Second split; now 3 hands
        hand_3 = hand_1.split_hand()
        player.add_hand(bj_hand=hand_3, split_limit=TestConfig.SPLIT_LIMIT)

        assert hand_3 is not None

        hand_1.add_card(Card('H', 'A'))
        hand_3.add_card(Card('S', 'A'))

        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_3) == 'SP'

        # Third split; now 4 hands; no more splits allowed
        hand_4 = hand_2.split_hand()
        player.add_hand(bj_hand=hand_4, split_limit=TestConfig.SPLIT_LIMIT)

        assert hand_4 is not None
        assert player.allowed_to_split is False

        hand_2.add_card(Card('D', 'A'))
        hand_4.add_card(Card('C', 'A'))

        # No more splits allowed so the action for all hands should be Hit
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_1) == 'H'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_2) == 'H'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_3) == 'H'
        assert sim.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=hand_4) == 'H'



if __name__ == '__main__':
    unittest.main()
