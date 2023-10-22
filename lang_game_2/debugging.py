from game_analysis import *

game = None
seed = None
timeout = 10000
amount_of_agents = 2
food_found = 0
# game = Game(timeout, amount_of_agents, seed=seed, gui=True)
# game.game_loop()
while food_found < 0.1 * timeout:
    timeout = 10000
    seed = random.randint(0, 1000)
    game = Game(timeout, amount_of_agents, seed=seed, gui=True)
    game.game_loop()
    food_found = game.robots[1].logs["food_found"]
    print(food_found)
    print(f"seed:{seed}")
game = Game(timeout, amount_of_agents, seed=seed, gui=True)
game.game_loop()
food_found = game.robots[1].logs["food_found"]
print(food_found)
print("done simulating")
analysis = GameAnalysis(game)
food_found_data = analysis.print_data()
given_instructions = analysis.show_instructions()
requester, fetcher = game.robots
vocab_chain = analysis.print_vocab_chain(requester, fetcher)
print("done analysing")
