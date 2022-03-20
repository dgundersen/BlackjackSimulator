import json
import logging
import time
from blackjack_sim.game_models import *
from blackjack_sim.strategy import Strategy
from blackjack_sim.errors import *
from blackjack_sim.utils import Utils


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

    SHOE_CUTOFF = 30  # if there are fewer than this many cards left then we get a new shoe

    def __init__(self, idx, sim_config, strategy_config):
        self.name = sim_config['name']
        self.num_decks = sim_config['num_decks']
        self.num_players = sim_config['num_players']
        self.num_sessions = sim_config['num_sessions']
        self.max_session_hands = sim_config['max_session_hands']
        self.min_bet = sim_config['min_bet']
        self.buyin_num_bets = sim_config['buyin_num_bets']
        self.verbose = True if 'verbose' in sim_config and int(sim_config['verbose']) == 1 else False

        self.strategy = Strategy(idx, strategy_config)

        self.shoe = []
        self.player_hands = []
        self.dealer_hand = None
        self.num_hands_played = 0

        self.session_idx = -1
        self.sessions = []

        log_level = logging.DEBUG if self.verbose else logging.INFO

        self.log = Utils.get_logger(f'Simulation-{idx}', log_level)

    def get_next_card(self):
        return self.shoe.pop(0)

    def run(self):
        self.log.info(f'\nRunning: {self.name}')

        start_time = time.perf_counter()

        try:
            for s in range(self.num_sessions):
                self.session_idx += 1
                self.sessions.append(BlackjackSession(
                    idx=self.session_idx,
                    num_players=self.num_players,
                    buyin=self.buyin_num_bets * self.min_bet
                ))

                for h in range(self.max_session_hands):
                    self.play_round()

            self.log_results()

        except Exception as ex:
            self.log.error(ex, exc_info=True)

        end_time = time.perf_counter()

        self.log.info(f"Finished in {end_time - start_time:0.4f} seconds")

    def log_all_hands(self):
        self.log.debug('')
        self.log_hand(self.dealer_hand, True)
        for player_hand in self.player_hands:
            self.log_hand(player_hand, False)

    def log_hand(self, bj_hand, is_dealer):
        hand_type_str = 'Dealer' if is_dealer else 'Player'
        self.log.debug(f'{hand_type_str}: {bj_hand} - {bj_hand.result}')
        if bj_hand.linked_hand:
            self.log_hand(bj_hand.linked_hand, is_dealer)

    def log_results(self):
        self.log.info('Results:')
        self.log.info(f'# Simulation hands: {self.num_hands_played}')
        self.log.info(f'# Sessions: {self.num_sessions}')
        self.log.info(f'# Players: {self.num_players}')

        for session in self.sessions:
            self.log.info(f'  # Session {session.session_idx} hands: {session.num_hands_played}')

            for p in session.players:
                self.log.info(f'    Player {p.player_idx}: {p.get_gameplay_result_str()}')

    def play_round(self):
        self.num_hands_played += 1
        self.sessions[self.session_idx].num_hands_played += 1

        # Check if we need a new shoe
        if len(self.shoe) < self.SHOE_CUTOFF:
            self.shoe = Shoe(self.num_decks).cards
            burn_card = self.get_next_card()

            self.log.debug(f'New shoe of {self.num_decks} decks, {len(self.shoe)} cards; burn card: {burn_card}')

        # Reset hands
        self.dealer_hand = BlackjackHand(idx=None, dealer_hand=True)
        self.player_hands = []
        for p in range(self.num_players):
            self.player_hands.append(BlackjackHand(idx=p, dealer_hand=False))

        # Deal 2 rounds of cards
        self.deal_round_of_cards()
        self.deal_round_of_cards()

        self.log_all_hands()

        dealer_up_card = self.dealer_hand.cards[0]

        # TODO: Pay 3 card bonus

        # Check if dealer has blackjack
        if self.dealer_hand.is_blackjack:
            for player_hand in self.player_hands:
                self.evaluate_hand_result(
                    player=self.sessions[self.session_idx].players[player_hand.player_idx],
                    player_hand=player_hand,
                    dealer_has_bj=True
                )

        else:
            # Play each player's hand
            for player_hand in self.player_hands:
                self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)

            # Play dealer's hand
            self.play_dealer_hand()

            # Evaluate each player's hand
            for player_hand in self.player_hands:
                self.evaluate_hand_result(
                    player=self.sessions[self.session_idx].players[player_hand.player_idx],
                    player_hand=player_hand,
                    dealer_has_bj=False
                )

        self.log_all_hands()

        # TODO: Pay bust bonus


    def deal_round_of_cards(self):
        # Deal to players
        for player_hand in self.player_hands:
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

                self.sessions[self.session_idx].players[player_hand.player_idx].record_hand_result(bj_hand_result=player_hand.result)

            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)

        # double
        elif action == 'D':
            # TODO: double bet
            player_hand.add_card(self.get_next_card())

        # split
        elif action == 'SP':
            player_hand.split_hand()
            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand)
            self.play_player_hand(dealer_up_card=dealer_up_card, player_hand=player_hand.linked_hand)

    def evaluate_hand_result(self, player, player_hand, dealer_has_bj):
        if dealer_has_bj:
            if player_hand.is_blackjack:
                player_hand.result = BlackjackHandResult.PUSH
            else:
                player_hand.result = BlackjackHandResult.LOSS

            player.record_hand_result(bj_hand_result=player_hand.result)

        else:
            if player_hand.result == BlackjackHandResult.UNDETERMINED:
                player_hand_value = player_hand.get_ultimate_value()
                dealer_hand_value = self.dealer_hand.get_ultimate_value()

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

                player.record_hand_result(bj_hand_result=player_hand.result)

            if player_hand.linked_hand:
                self.evaluate_hand_result(
                    player=player,
                    player_hand=player_hand.linked_hand,
                    dealer_has_bj=dealer_has_bj
                )

