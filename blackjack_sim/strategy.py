from blackjack_sim.game_models import Card
from blackjack_sim.errors import *


class Strategy(object):

    def __init__(self, strategy_config):
        self.hard_totals = {}  # dict; key=total, val=action
        self.soft_hands = {}  # dict; key=hand, val=action
        self.pairs = {}  # dict; key=hand, val=action

        if 'hard_totals' in strategy_config and strategy_config['hard_totals']:
            for key, value in strategy_config['hard_totals'].items():
                if len(value) != 10:
                    raise ConfigurationError(f'Invalid # of actions in hard_totals for: {key}')
                else:
                    hand_total = int(key)
                    self.hard_totals[hand_total] = value
        else:
            raise ConfigurationError('Missing hard_totals in strategy config')

        if 'soft_hands' in strategy_config and strategy_config['soft_hands']:
            for key, value in strategy_config['soft_hands'].items():
                if len(value) != 10:
                    raise ConfigurationError(f'Invalid # of actions in soft_hands for: {key}')
                else:
                    self.soft_hands[key] = value
        else:
            raise ConfigurationError('Missing soft_hands in strategy config')

        if 'pairs' in strategy_config and strategy_config['pairs']:
            for key, value in strategy_config['pairs'].items():
                if len(value) != 10:
                    raise ConfigurationError(f'Invalid # of actions in pairs for: {key}')
                else:
                    self.pairs[key] = value
        else:
            raise ConfigurationError('ERROR: Missing pairs in strategy config')

    def determine_player_action(self, dealer_up_card, player_hand):
        num_cards = len(player_hand.cards)
        hand_cards = player_hand.get_hand_as_ranks()
        dealer_up_card_idx = Card.get_dealer_up_card_index(dealer_up_card)

        action = None
        # Determine the player's first action for the hand
        # Look up pairs first (if still allowed to split), then soft hands, then hard totals; this order matters.
        if num_cards == 2:
            if player_hand.is_blackjack:
                action = 'S'
            elif player_hand.player.allowed_to_split and hand_cards in self.pairs.keys():
                action = self.pairs[hand_cards][dealer_up_card_idx]
            elif hand_cards in self.soft_hands.keys():
                action = self.soft_hands[hand_cards][dealer_up_card_idx]
            elif player_hand.hard_value in self.hard_totals.keys():
                action = self.hard_totals[player_hand.hard_value][dealer_up_card_idx]

        # Determine the player's action after initially hitting
        # Stand on soft 19 or greater, otherwise follow hard totals strategy and either hit or stand
        # TODO: do we need to add another strategy config for this?
        elif num_cards > 2:
            if player_hand.soft_value and player_hand.soft_value >= 19:
                return 'S'
            elif player_hand.hard_value in self.hard_totals.keys():
                action = self.hard_totals[player_hand.hard_value][dealer_up_card_idx]

                if action == 'D':
                    action = 'H'

        # There will only be 1 card if we just split
        elif num_cards == 1:
            return 'H'

            # Return action of stand if we're at 21 or busted
        if player_hand.hard_value >= 21:
            action = 'S'

        if not action:
            raise DetermineActionError(f'Unable to determine player action for hand: {hand_cards}')

        return action


