import json
import logging
import time
from blackjack_sim.game_models import *
from blackjack_sim.strategy import Strategy
from blackjack_sim.utils import Utils
from blackjack_sim.bonuses import *


class SimulationManager(object):

    def __init__(self):
        self.simulations = []

        self.log = Utils.get_logger('SimulationManager', logging.INFO)

        # load main config file; contains 1 or more simulations
        sim_config_list = self.load_json_file('blackjack_sim/config/simulation_config.json')

        if sim_config_list:
            for sim_config in sim_config_list:
                # load strategy config
                if 'strategy_config_file' in sim_config and sim_config['strategy_config_file']:
                    strategy_config = self.load_json_file(sim_config['strategy_config_file'])

                    if strategy_config:
                        self.simulations.append(Simulation(len(self.simulations), sim_config, strategy_config))
                    else:
                        self.log.error('ERROR: Unable to load strategy config file')
                else:
                    self.log.error('ERROR: No strategy config file')

            self.log.info(f'Loaded {len(self.simulations)} simulations')
        else:
            self.log.error('ERROR: Unable to load simulation config file')

    def load_json_file(self, file_name_and_path):
        json_file = None

        try:
            with open(file_name_and_path, 'r') as f:
                json_file = json.load(f)
        except Exception as ex:
            self.log.error(ex, exc_info=False)

        return json_file

    def run_simulations(self):
        for sim in self.simulations:
            sim.run()

class Simulation(object):

    MINOR_LOG_SEPARATOR = '---------------------------------------------------------------------------------------'
    MAJOR_LOG_SEPARATOR = '======================================================================================='

    SHOE_CUTOFF = 30  # if there are fewer than this many cards left then we get a new shoe

    def __init__(self, idx, sim_config, strategy_config):
        self.name = sim_config['name']
        self.num_decks = sim_config['num_decks']
        self.num_players = sim_config['num_players']
        self.num_sessions = sim_config['num_sessions']
        self.max_session_hands = sim_config['max_session_hands']
        self.min_bet = sim_config['min_bet']
        self.buyin_num_bets = sim_config['buyin_num_bets']
        self.split_limit = int(sim_config['split_limit']) if 'split_limit' in sim_config else None
        self.verbose = True if 'verbose' in sim_config and int(sim_config['verbose']) == 1 else False

        self.strategy = Strategy(strategy_config)

        # Bonus bets are really more strategy but putting it in sim config makes it easier
        # to compare simulations of playing vs not playing bonus bets.
        self.bonus_payer_21_3 = None
        self.bonus_payer_bust = None
        self.bonus_bet_config = None
        if 'bonus_bets' in sim_config:
            self.bonus_bet_config = sim_config['bonus_bets']

            if '21_3' in sim_config['bonus_bets']:
                self.bonus_payer_21_3 = TwentyOne3BonusPayer()

            if 'bust' in sim_config['bonus_bets']:
                self.bonus_payer_bust = BustBonusPayer()

        self.shoe_factory = ShoeFactory(self.num_decks)

        self.shoe = []
        self.dealer_hand = None
        self.num_hands_played = 0
        self.num_shoes_used = 0

        self.sessions = []
        self.current_session = None

        log_level = logging.DEBUG if self.verbose else logging.INFO

        self.log = Utils.get_logger(f'Simulation-{idx}', log_level)

    def get_next_card(self):
        if len(self.shoe) == 0:
            self.log.warn('WARNING: Tried to get card from empty shoe')

            self.new_shoe()

        return self.shoe.pop(0)

    def run(self):
        self.log.info(self.MAJOR_LOG_SEPARATOR)
        self.log.info(f'\nRunning: {self.name}')

        start_time = time.perf_counter()

        try:
            for s in range(self.num_sessions):

                self.current_session = BlackjackSession(
                    idx=s,
                    num_players=self.num_players,
                    buyin=self.buyin_num_bets * self.min_bet,
                    bonus_config=self.bonus_bet_config
                )

                self.sessions.append(self.current_session)

                for h in range(self.max_session_hands):
                    # Show progress for large numbers of hands
                    if self.max_session_hands >= 10000:
                        if h % 10000 == 0:
                            self.log.info(f'playing hand {h}')

                    self.play_round()

            self.log_results()
            self.log.info(self.MINOR_LOG_SEPARATOR)

        except Exception as ex:
            self.log.error(ex, exc_info=True)

        end_time = time.perf_counter()

        self.log.info(f"Finished in {end_time - start_time:0.4f} seconds")
        self.log.info(self.MAJOR_LOG_SEPARATOR)

    def log_all_hands(self):
        self.log.debug('')
        self.log_hand(self.dealer_hand, True)
        for player in self.current_session.players:
            for player_hand in player.hands:
                self.log_hand(player_hand, False)

    def log_hand(self, bj_hand, is_dealer):
        hand_type_str = 'Dealer' if is_dealer else 'Player'
        self.log.debug(f'{hand_type_str}: {bj_hand} - {bj_hand.result}')

    def log_results(self):
        self.log.info(self.MAJOR_LOG_SEPARATOR)
        self.log.info('Simulation Results:')
        self.log.info(f'# Hands: {self.num_hands_played}')
        self.log.info(f'# Shoes: {self.num_shoes_used}')
        self.log.info(f'# Sessions: {self.num_sessions}')
        self.log.info(f'# Players: {self.num_players}')

        for session in self.sessions:
            self.log.info(self.MAJOR_LOG_SEPARATOR)
            self.log.info(f'# Session {session.session_idx} hands: {session.num_hands_played}')

            for p in session.players:
                result_str = p.get_gameplay_result_str(min_bet=self.min_bet)
                self.log.info(self.MINOR_LOG_SEPARATOR)
                self.log.info(result_str)

    def new_shoe(self):
        self.num_shoes_used += 1
        self.shoe = self.shoe_factory.get_shoe()
        burn_card = self.get_next_card()

        self.log.debug(f'New shoe of {self.num_decks} decks, {len(self.shoe)} cards; burn card: {burn_card}')

    def reset_hands_for_next_round(self):
        self.dealer_hand = BlackjackHand(player=None, dealer_hand=True)
        for player in self.current_session.players:
            player.reset_hands()
            player.add_hand(
                bj_hand=BlackjackHand(player=player, dealer_hand=False, bet=self.min_bet),
                split_limit=self.split_limit
            )

    def play_round(self):

        # TODO: quit when broke when that option is enabled

        self.num_hands_played += 1
        self.current_session.num_hands_played += 1

        # Check if we need a new shoe
        if len(self.shoe) < self.SHOE_CUTOFF:
            self.new_shoe()

        # Reset hands
        self.reset_hands_for_next_round()

        # Deal 2 rounds of cards
        self.deal_round_of_cards()
        self.deal_round_of_cards()

        if self.verbose:
            self.log_all_hands()

        dealer_up_card = self.dealer_hand.cards[0]

        # Get starting hands before playing/splitting
        starting_hands = []
        for player in self.current_session.players:
            for player_hand in player.hands:
                starting_hands.append(player_hand)

                # Pay 3 card bonus if configured
                if player.will_play_21_3_bonus():
                    bonus_payout = self.bonus_payer_21_3.get_payout(
                        dealer_up_card=dealer_up_card,
                        player_hand=player_hand,
                        bonus_bet=player.bonus_plan_21_3.get_bet_amount()
                    )

                    player.record_21_3_bonus_result(payout=bonus_payout)

        # Check if dealer has blackjack
        if self.dealer_hand.is_blackjack:
            for player_hand in starting_hands:
                self.evaluate_hand_result(
                    player_hand=player_hand,
                    dealer_hand=self.dealer_hand
                )

        else:
            # Play each player's hand
            for player_hand in starting_hands:
                self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)

            # Play dealer's hand
            self.play_dealer_hand()

            # Evaluate each player's hand; get from players, not starting hands
            for player in self.current_session.players:
                for player_hand in player.hands:
                    self.evaluate_hand_result(
                        player_hand=player_hand,
                        dealer_hand=self.dealer_hand
                    )

                # Pay bust bonus if configured
                if player.will_play_bust_bonus(dealer_up_card=dealer_up_card):
                    bonus_payout = self.bonus_payer_bust.get_payout(
                        dealer_hand=self.dealer_hand,
                        bonus_bet=player.bonus_plan_bust.get_bet_amount(dealer_up_card=dealer_up_card)
                    )

                    player.record_bust_bonus_result(payout=bonus_payout, dealer_up_card=dealer_up_card)

        if self.verbose:
            self.log_all_hands()


    def deal_round_of_cards(self):
        # Deal to players
        for player in self.current_session.players:
            for player_hand in player.hands:
                player_hand.add_card(self.get_next_card())

        # Dealer takes card
        self.dealer_hand.add_card(self.get_next_card())

    def play_dealer_hand(self):
        action = self.determine_dealer_action()

        self.log.debug(f'Playing dealer hand {self.dealer_hand}, Action: {action}')

        # stand
        if action == 'S':
            return

        # hit
        elif action == 'H':
            self.dealer_hand.add_card(self.get_next_card())
            self.play_dealer_hand()

    def determine_dealer_action(self):
        if self.dealer_hand.soft_value and self.dealer_hand.soft_value > 17:
            return 'S'
        elif self.dealer_hand.hard_value >= 17:
            return 'S'
        else:
            return 'H'

    def play_player_hand(self, dealer_up_card, player_hand):
        action = self.strategy.determine_player_action(dealer_up_card=dealer_up_card, player_hand=player_hand)

        self.log.debug(f'Playing player hand {player_hand}, Action: {action}')

        # stand
        if action == 'S':
            return

        # hit
        elif action == 'H':
            player_hand.add_card(self.get_next_card())

            # Check if we busted
            if player_hand.hard_value > 21:
                player_hand.result = BlackjackHandResult.LOSS

                player_hand.player.record_hand_result(bj_hand=player_hand)

            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)

        # double
        elif action == 'D':
            player_hand.bet *= 2
            player_hand.add_card(self.get_next_card())

        # split
        elif action == 'SP':
            new_hand = player_hand.split_hand()

            player_hand.player.add_hand(bj_hand=new_hand, split_limit=self.split_limit)

            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)
            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=new_hand)

    def evaluate_hand_result(self, player_hand, dealer_hand):
        if dealer_hand.is_blackjack:
            if player_hand.is_blackjack:
                player_hand.result = BlackjackHandResult.PUSH
            else:
                player_hand.result = BlackjackHandResult.LOSS

            player_hand.player.record_hand_result(bj_hand=player_hand)

        else:
            if player_hand.result == BlackjackHandResult.UNDETERMINED:
                player_hand_value = player_hand.get_ultimate_value()
                dealer_hand_value = dealer_hand.get_ultimate_value()

                if self.dealer_hand.hard_value > 21:
                    player_hand.result = BlackjackHandResult.WIN
                elif player_hand.is_blackjack:
                    player_hand.result = BlackjackHandResult.WIN
                elif player_hand_value > dealer_hand_value:
                    player_hand.result = BlackjackHandResult.WIN
                elif player_hand_value == dealer_hand_value:
                    player_hand.result = BlackjackHandResult.PUSH
                elif player_hand_value < dealer_hand_value:
                    player_hand.result = BlackjackHandResult.LOSS

                player_hand.player.record_hand_result(bj_hand=player_hand)


