from game_analysis import GameAnalysis
from game import Game
from game import random


def find_passable_game(timeout, num_of_agents):
    simulated_game = None
    done = False
    while not done:
        seed = random.randint(0, 1000)
        simulated_game = Game(timeout, num_of_agents, seed, gui=False)
        simulated_game.game_loop()
        print(f"food found: {simulated_game.average_found_food}")
        print(f"seed:{simulated_game.seed}")
        if simulated_game.average_found_food > 0.1*timeout:
            break
        # done = True
    return simulated_game


initial_timeout = 100
amount_of_agents = 2

passable_game = find_passable_game(initial_timeout, amount_of_agents)
print("showing simulation")

# game = Game(initial_timeout, amount_of_agents, passable_game.seed, gui=True)
# game.game_loop()
# print(f"food found: {game.average_found_food}")
# print("done simulating")
#
# analysis = GameAnalysis(game)
# food_found_data = analysis.print_data()
# given_instructions = analysis.show_instructions()
# requester, fetcher = game.robots
# vocab_chain = analysis.print_vocab_chain(requester, fetcher)
# print("done analysing")
