from blackjack_sim.errors import *


class Strategy(object):

    def __init__(self, idx, strategy_config):
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

