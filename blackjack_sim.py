from blackjack_sim.game_manager import GameManager

def run_simulation():

    print('Running')

    game_mgr = GameManager()

    shoe = []
    for i in range(game_mgr.num_decks):
        deck = GameManager.get_deck()
        for card in deck:
            shoe.append(card)

    print(f'Got shoe of {game_mgr.num_decks} decks, {len(shoe)} cards')




if __name__ == '__main__':
    run_simulation()
