import multiprocessing as mp
from multiprocessing import Pool, Manager

from game_analysis import GameAnalysis
from game import Game
from game import random


def generate_random_seeds(amount):
    seeds = set()
    while len(seeds) < amount:
        seeds.add(random.randint(0, 10000))
    return seeds


def run_set_game(timeout: int, num_of_agents: int, seed: int, gui: bool = False):
    simulated_game = Game(timeout, num_of_agents, seed, gui)
    simulated_game.game_loop()
    return simulated_game


def find_passable_game(initial_timeout, num_agents, seed, stop_event, passable_seed):
    if not stop_event.is_set():
        simulated_game = run_set_game(initial_timeout, num_agents, seed)
        if simulated_game.average_found_food > 0.1 * initial_timeout and not stop_event.is_set():
            print(f"\nseed:{simulated_game.seed} - average food found: {simulated_game.average_found_food}")
            passable_seed.value = simulated_game.seed
            stop_event.set()
            return simulated_game.seed
        else:
            if not stop_event.is_set():
                print(f"{simulated_game.average_found_food}", end=" ")


if __name__ == '__main__':
    with Manager() as manager:
        initial_timeout = 1000
        num_agents = 2
        num_cpu = mp.cpu_count()
        stop_event = manager.Event()
        passable_seed = manager.Value("i", -1)
        with Pool(num_cpu) as pool:
            seeds = list(generate_random_seeds(10000))
            random.shuffle(seeds)
            iterations = [[initial_timeout, num_agents, seed, stop_event, passable_seed] for seed in seeds]
            result = pool.starmap_async(find_passable_game, iterations)
            result.wait()
        print(passable_seed.value)
        game = Game(initial_timeout, num_agents, passable_seed.value, gui=True)
        game.game_loop()
        print(f"food found: {game.average_found_food}")
        print("done simulating")
        analysis = GameAnalysis(game)
        food_found_data = analysis.print_data()
        given_instructions = analysis.show_instructions()
        requester, fetcher = game.robots
        vocab_chain = analysis.print_vocab_chain(requester, fetcher)
        print("done analysing")
