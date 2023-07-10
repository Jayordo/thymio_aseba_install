from game import *

lg = Game(100)
timeout = 10000


while timeout > 0:
    lg.play_game_with_two_agents(*lg.select_two_random_agents())
    print(f"\nt-plus {timeout}")
    timeout -= 1
