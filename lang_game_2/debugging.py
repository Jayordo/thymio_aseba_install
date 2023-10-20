from game_analysis import *

game = None
seed = None
timeout = 500
amount_of_agents = 3
food_found = 0
while food_found < 0.5 * timeout:
    seed = random.randint(0, 1000)
    game = Game(timeout, amount_of_agents, seed=seed, gui=False)
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
# requester, fetcher = game.robots
# vocab_chain = analysis.print_vocab_chain(requester, fetcher)
print("done analysing")
