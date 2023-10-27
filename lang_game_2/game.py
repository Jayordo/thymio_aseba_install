import numpy as np
import random
# import pygame
from agent import Agent
from maze import Maze
from line_profiler_pycharm import profile
from feature import Feature


class Game:
    def __init__(self, timeout: int, amount_of_agents: int, seed: int, gui: bool = False):
        # given
        random.seed(seed)
        np.random.seed(seed)
        self.seed = seed
        self.timeout = timeout
        self.amount_of_agents = amount_of_agents
        self.gui = gui
        # inits
        self.stop_command = False
        self.current_requested_food = None
        self.action_buckets = None
        self.last_hundred_results = []
        # statics
        self.arena_size = 8
        difficulty = 0.5
        fps = 0
        self.max_chain_length = 1
        self.max_sentence_length = 10
        self.amount_of_instructions_in_features = 2
        self.params = dict({
            "action_types": [],
            "reward_factor": 20,
            "punish_factor": 1
        })
        # startup functions
        self.maze = Maze(self.amount_of_agents, self.arena_size, difficulty, gui, fps)
        self.food_types = self.set_food_types(2)
        self.prepare_params()
        self.robots = self.generate_robots()
        self.set_new_food()

    def set_food_types(self, amount_of_food_types: int):
        food_types = []
        for food_type in range(amount_of_food_types):
            name = (-1, food_type)
            self.maze.add_food(name)
            food_types.append(name)
        return food_types

    def prepare_params(self):
        self.action_buckets = dict({
            "movement_buckets": 10,
            "rotation_buckets": 10,
            # "speech_buckets": 10,
            # "stop_talking_buckets": 2
        })
        for _, amount in self.action_buckets.items():
            self.params["action_types"].append((0, amount))

    def generate_robots(self):
        letter = 65
        robots = []
        for rob_id in range(self.amount_of_agents):
            name = chr(letter + rob_id)
            rob = Agent(name, self.params)
            self.maze.add_player(name)
            robots.append(rob)
        return robots

    def set_new_food(self):
        self.current_requested_food = random.choice(self.food_types)
        self.maze.current_requested_food = self.current_requested_food

    def listen_around(self, rob: Agent):
        used_robs = set()
        while len(used_robs) < len(self.robots):
            rob2 = random.choice(self.robots)
            if rob2 not in used_robs:
                used_robs.add(rob2)
                if rob is not rob2:
                    if rob2.role == "requester":
                        # once distance matters again redo this
                        # if self.distance_to(rob.location, rob2.location) < self.close_enough:
                        return rob2
        return None

    @profile
    def collect_instructions(self, fetcher: Agent, requester: Agent):
        # possible eventually merge this with execute action and execute actions
        word_count = 0
        while word_count <= self.max_sentence_length:
            self.generate_env_features(requester)
            response = requester.parse_input(self.current_requested_food)
            fetcher.current_instructions.append(response)

            word_count += 1
        fetcher.current_instructions_received_from = requester.name

    def evaluate(self, fetcher: Agent):
        if self.maze.is_player_colliding_with_food(fetcher.name, self.current_requested_food):
            fetcher.found_food = True

    @staticmethod
    @profile
    def reward_or_punish_robs(fetcher: Agent, requester: Agent):
        punish = False if fetcher.found_food else True
        f_instructions_index = len(fetcher.last_subsequent_instructions) - 1
        for i_i, r_instruction in enumerate(requester.last_subsequent_instructions):
            r_action = requester.last_subsequent_actions[i_i]
            requester.reward_or_punish(r_instruction, r_action, punish)
            # maybe test if this hits everything
            if i_i > f_instructions_index:
                break
            f_instruction = fetcher.last_subsequent_instructions[i_i]
            f_action = fetcher.last_subsequent_actions[i_i]
            fetcher.reward_or_punish(f_instruction, f_action, punish)

    def game_loop(self):
        self.kill_command(self.maze.keypress_handler())
        while self.timeout > 0 and not self.stop_command:
            self.kill_command(self.maze.keypress_handler())
            self.maze.gui_timer()
            for rob in self.robots:
                if self.stop_command:
                    break
                self.start_of_turn_handler(rob)
                while rob.current_chain_length <= self.max_chain_length and not rob.found_food:
                    requester = self.listen_around(rob)
                    if requester:
                        self.collect_instructions(rob, requester)
                        self.execute_instructions(rob)
                        self.reward_or_punish_robs(rob, requester)
                    else:
                        rob.role = "requester"

                    rob.current_chain_length += 1
            self.timeout -= 1
            self.end_of_round_handler()
        self.end_of_game_handler()

    def kill_command(self, kill: bool):
        if kill:
            self.stop_command = True

    def start_of_turn_handler(self, rob: Agent):
        rob.reset_to_init()
        self.reset_position(rob)
        rob.last_subsequent_locations.append(self.maze.get_player_copy(rob.name))
        self.maze.update_caption([self.timeout, self.total_found_food, sum(self.last_hundred_results)])

    def reset_position(self, rob: Agent):
        rob.rotation = 0
        self.maze.return_to_spawn(rob.name)

    def end_of_round_handler(self):
        self.kill_command(self.maze.keypress_handler())
        for rob in self.robots:
            rob.write_to_logs()
            rob.clear_instructions()
            if rob.found_food:
                self.set_new_food()
                self.last_hundred_results.append(1)
            else:
                self.last_hundred_results.append(0)
        if len(self.last_hundred_results) > 100:
            self.last_hundred_results = self.last_hundred_results[1:]

    def end_of_game_handler(self):
        self.maze.kill_pygame()

    @profile
    def execute_instructions(self, rob: Agent):
        for instruction_id, instruction in enumerate(rob.current_instructions):
            self.kill_command(self.maze.keypress_handler())
            self.generate_env_features(rob)
            action = rob.parse_input(instruction)
            self.execute_action(rob, *action)
            if rob.found_food:
                rob.current_instructions = rob.current_instructions[:instruction_id + 1]
                return

    @profile
    def execute_action(self, rob: Agent, action_type: int, amount: int):
        if action_type == 0:
            radians = np.deg2rad(rob.rotation)
            c, s = np.cos(radians), np.sin(radians)
            for i in range(amount):
                self.evaluate(rob)
                if rob.found_food:
                    return
                self.maze.move(rob.name, c, s)
            rob.last_subsequent_locations.append(self.maze.get_player_copy(rob.name))
        elif action_type == 1:
            degrees_per_bucket = 360 / len(range(*self.params["action_types"][1]))
            rob.rotation = (rob.rotation + (int(amount * degrees_per_bucket))) % 360

    def generate_env_features(self, rob: Agent):
        last_action = (-1, -1) if len(rob.last_subsequent_actions) == 0 else rob.last_subsequent_actions[-1]
        last_instruction = (-1, -1) if len(rob.last_subsequent_instructions) == 0 else rob.last_subsequent_instructions[
            -1]
        f1 = Feature([self.maze.calculate_distance_to_forward_block(rob.name)], [float])
        f1.normalise(0, self.arena_size)
        f2 = Feature([rob.rotation], [int])
        f2.normalise(0, self.action_buckets["rotation_buckets"])
        f3 = Feature(last_action, [bool, int])
        f3.normalise(0, self.action_buckets["movement_buckets"])
        f4 = Feature(last_instruction, [bool, bool])
        f5 = Feature([rob.current_instructions_received_from], [bool])
        features = [
            # f1,
            f2,
            # f3,
            # f4,
            # f5
            # colour ray casting or percentage of vision ray-casting
        ]

        # added_zeroes = (self.amount_of_instructions_in_features - instruction_id)*[0]
        # floor = 0 if len(added_zeroes)==0 else instruction_id-self.amount_of_instructions_in_features
        # # test if always puts out same length
        # padded_instructions = added_zeroes + rob.current_instructions[floor:instruction_id+self.amount_of_instructions_in_features+1] + added_zeroes
        # added_zeroes = added_zeroes[:-1]_
        # floor = 0 if len(added_zeroes) == 0 else instruction_id - self.amount_of_instructions_in_features+1
        # padded_actions = rob.last_subsequent_actions[floor:]
        # features = features + padded_instructions + padded_actions

        # normalise features here
        rob.current_env_features = features

    @property
    def total_found_food(self):
        return sum([rob.logs["food_found"] for rob in self.robots if rob.role == "fetcher"])

    @property
    def average_found_food(self):
        return self.total_found_food / sum([1 for rob in self.robots if rob.role == "fetcher"])
