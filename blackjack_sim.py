import sys
import logging
from blackjack_sim.simulation import SimulationManager
from blackjack_sim.utils import Utils

def run_simulation():
    log = Utils.get_logger('BlackjackSimulator', logging.INFO)

    log.info('Running BlackjackSimulator')

    sim_mgr = SimulationManager(sim_config_file_path=sys.argv[1] if len(sys.argv) > 1 else None)

    sim_mgr.run_simulations()


if __name__ == '__main__':
    run_simulation()
