from blackjack_sim.game_manager import GameManager

def run_simulation():

    print('Running')

    num_decks = 6  # TODO: get from config

    shoe = []
    for i in range(num_decks):
        deck = GameManager.get_deck()
        for card in deck:
            shoe.append(card)

    print(f'Got shoe of {num_decks} decks, {len(shoe)} cards')




if __name__ == '__main__':
    run_simulation()
