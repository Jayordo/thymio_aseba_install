import numpy as np
import random
import pygame
from agent import Agent
from maze import Maze


class Game:
    def __init__(self, timeout, amount_of_agents,seed, gui=False):
        # given
        random.seed(seed)
        np.random.seed(seed)
        self.timeout = timeout
        self.amount_of_agents = amount_of_agents
        self.gui = gui
        # empties
        self.current_requested_food = None
        self.action_buckets = None
        self.last_hundred_results = []
        # statics
        self.arena_size = 8
        self.difficulty = 0.5
        self.fps = 0
        self.chain_length = 1
        self.max_sentence_length = 20
        self.amount_of_instructions_in_features = 2
        self.possible_roles = [
            "requester",
            "fetcher"
        ]
        self.params = dict({
            "action_types": [],
            "reward_factor": 20,
            "punish_factor": 1
        })
        # startup functions
        self.maze = Maze(self.amount_of_agents, self.arena_size, self.difficulty, self.gui)
        self.food_types = self.set_food_types(2)
        self.prepare_params()
        self.robots = self.generate_robots()

    def set_food_types(self, amount_of_food_types: int):
        food_types = []
        for food_type in range(amount_of_food_types):
            name = (-1,food_type)
            self.maze.add_food(name)
            food_types.append(name)
        return food_types

    def prepare_params(self):
        self.action_buckets = dict({
            "move_buckets": 9,
            "rotation_buckets": 9,
            "nothing_buckets": 5,
            # "speech_buckets": 10,
            # "stop_talking_buckets": 2
        })
        for k, v in self.action_buckets.items():
            self.params["action_types"].append((1, v + 1))

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

    def assign_role(self, rob):
        if not self.listen_around(rob):
            rob.role = "requester"
        else:
            rob.role = "fetcher"

    def listen_around(self, rob: Agent):
        used_robs = set()
        while len(used_robs) < len(self.robots):
            rob2 = random.choice(self.robots)
            if rob2 not in used_robs:
                used_robs.add(rob2)
                if rob is not rob2:
                    if rob2.speaking:
                        # if self.distance_to(rob.location, rob2.location) < self.close_enough:
                        return rob2
        return None

    def collect_instructions(self, fetcher: Agent, requester: Agent):
        requester.clear_instructions()
        fetcher.clear_instructions()
        env_features = self.generate_env_features(fetcher)
        given_sentence = requester.generate_sentence(self.current_requested_food, self.max_sentence_length,
                                                     env_features)
        fetcher.instructions = given_sentence
        fetcher.instructions_received_from = requester.name

    def evaluate(self, fetcher: Agent):
        if self.maze.is_player_colliding_with_food(fetcher.name, self.current_requested_food):
            fetcher.found_food = True

    @staticmethod
    def reward_or_punish_robs(fetcher: Agent, requester: Agent):
        punish = False if fetcher.found_food else True
        for i_i, r_instruction in enumerate(requester.last_subsequent_instructions):
            r_action = requester.last_subsequent_actions[i_i]
            requester.reward_or_punish(r_instruction, r_action, punish)
        # for i_i, f_instruction in enumerate(fetcher.last_subsequent_instructions):
            #maybe test if this hits everything
            if i_i > len(fetcher.last_subsequent_instructions)-1:
                break
            f_instruction = fetcher.last_subsequent_instructions[i_i]
            f_action = fetcher.last_subsequent_actions[i_i]
            fetcher.reward_or_punish(f_instruction, f_action, punish)

    def game_loop(self):
        turns_to_skip = None
        paused = False

        self.set_new_food()
        while self.timeout > 0:
            if turns_to_skip is None:
                pass
            elif turns_to_skip > 0:
                turns_to_skip -= 1
            else:
                self.gui = True
                turns_to_skip = None
            if not paused:
                # print(self.timeout)
                for rob in self.robots:
                    if not rob.role:
                        self.assign_role(rob)
                    if rob.role == "requester":
                        self.requesters_turn(rob)
                    elif rob.role == "fetcher":
                        self.fetchers_turn(rob)
                self.timeout -= 1
            # Put all this stuff in a different function
            if len(self.last_hundred_results) > 100:
                self.last_hundred_results = self.last_hundred_results[1:]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.timeout = -1
                if event.type == pygame.KEYDOWN:
                    if pygame.key.name(event.key) == "space":  # Pausing
                        if paused:
                            paused = False
                        else:
                            paused = True
                    if pygame.key.name(event.key) == "f":
                        turns_to_skip = 100
                        self.gui = False
                    if pygame.key.name(event.key) == "g":
                        turns_to_skip = 1000
                        self.gui = False
                    if pygame.key.name(event.key) == "x":
                        self.gui = False
                        pygame.display.set_mode(flags=pygame.HIDDEN)
                        turns_to_skip = None
                    print(pygame.key.name(event.key))
            if self.gui:

                pygame.display.set_caption(f'{self.timeout} {rob.logs["food_found"]} {sum(self.last_hundred_results)}%')

    def requesters_turn(self, requester: Agent):
        requester.speaking = requester.parse_input(self.current_requested_food, self.generate_env_features(requester))

    def fetchers_turn(self, fetcher: Agent):
        limit = self.chain_length
        requester = self.listen_around(fetcher)
        if not requester:
            fetcher.role = "requester"
            return
        while limit > 0 and requester and not fetcher.found_food:
            fetcher.logs["interactions_had"] += 1
            requester.logs["interactions_had"] += 1
            self.collect_instructions(fetcher, requester)
            self.execute_multiple_instructions(fetcher)
            limit -= 1
            requester = self.listen_around(fetcher)
        self.reward_or_punish_robs(fetcher, requester)
        if fetcher.found_food:
            self.set_new_food()
            self.last_hundred_results.append(1)
        else:
            self.last_hundred_results.append(0)
        fetcher.reset_and_log()
        self.maze.return_to_spawn(fetcher.name)
        return

    def execute_multiple_instructions(self, rob: Agent):
        rob.last_subsequent_locations.append(self.maze.get_player_copy(rob.name))
        for instruction_id, instruction in enumerate(rob.instructions):
            action = rob.parse_input(instruction, self.generate_env_features(rob))
            self.execute_action(rob, *action)
            rob.last_subsequent_locations.append(self.maze.get_player_copy(rob.name))
            self.evaluate(rob)
            if rob.found_food:
                rob.instructions = rob.instructions[:instruction_id + 1]
                return

    def execute_action(self, rob: Agent, action_type, amount):
        if action_type == 0:
            radians = np.deg2rad(rob.rotation)
            c, s = np.cos(radians), np.sin(radians)

            for i in range(amount):
                self.evaluate(rob)
                if rob.found_food:
                    return
                self.maze.move(rob.name, c, s)
                if self.gui:
                    self.maze.clock.tick(self.fps)
                    self.maze.show()
        elif action_type == 1:
            degrees_per_bucket = 360 / len(range(*self.params["action_types"][1]))
            rob.rotation = (rob.rotation + (int(amount * degrees_per_bucket))) % 360
        elif action_type == 2:
            return

    def generate_env_features(self, rob):

        last_action = (-1,-1) if len(rob.last_subsequent_actions) == 0 else rob.last_subsequent_actions[-1]
        last_instruction = (-1,-1) if len(rob.last_subsequent_instructions) == 0 else rob.last_subsequent_instructions[-1]
        features = [
            # rob.instructions_received_from,
            self.maze.calculate_distance_to_forward_block(rob.name),
            rob.rotation,
            #colour ray casting or percentage of vision raycasting
        ]
        to_be_unzipped = last_action,last_instruction
        for zipped_feature in to_be_unzipped:
            for feature in zipped_feature:
                features.append(feature)

        # added_zeroes = (self.amount_of_instructions_in_features - instruction_id)*[0]
        # floor = 0 if len(added_zeroes)==0 else instruction_id-self.amount_of_instructions_in_features
        # # test if always puts out same length
        # padded_instructions = added_zeroes + rob.instructions[floor:instruction_id+self.amount_of_instructions_in_features+1] + added_zeroes
        # added_zeroes = added_zeroes[:-1]
        # floor = 0 if len(added_zeroes) == 0 else instruction_id - self.amount_of_instructions_in_features+1
        # padded_actions = rob.last_subsequent_actions[floor:]
        # features = features + padded_instructions + padded_actions

        # normalise features here
        return features

