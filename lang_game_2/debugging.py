from game_analysis import GameAnalysis
from game import Game
from game import random
# import random


game = None
seed = None
initial_timeout = 100
amount_of_agents = 2
food_found = 0
# game = Game(timeout, amount_of_agents, seed=seed, gui=True)
# game.game_loop()
timeout = initial_timeout
done = False
while food_found < 0.1 * timeout and not done:
    timeout = initial_timeout
    seed = random.randint(0, 1000)
    # seed = 379
    game = Game(timeout, amount_of_agents, seed, gui=False)
    game.game_loop()
    food_found = game.robots[1].logs["food_found"]
    print(food_found)
    print(f"seed:{seed}")
    done = True
print("simulating")
game = Game(initial_timeout, amount_of_agents, seed, gui=True)
game.game_loop()
food_found = game.robots[1].logs["food_found"]
print(food_found)
print(f"seed:{seed}")
print("done simulating")
analysis = GameAnalysis(game)
food_found_data = analysis.print_data()
given_instructions = analysis.show_instructions()
requester, fetcher = game.robots
vocab_chain = analysis.print_vocab_chain(requester, fetcher)
print("done analysing")
