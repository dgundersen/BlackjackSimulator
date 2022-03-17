from blackjack_sim.simulation import SimulationManager

def run_simulation():

    print('Running BlackjackSimulator')

    sim_mgr = SimulationManager()

    sim_mgr.run_simulations()


if __name__ == '__main__':
    run_simulation()
