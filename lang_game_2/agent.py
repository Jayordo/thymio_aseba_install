from typing import Any

import numpy as np
import random

from numpy import ndarray, dtype


class Agent:
    def __init__(self, name: str, params: dict):
        self.params = params
        self.name = name
        self.vocab = dict()
        # vocab looks like:
        # (input_tuple): (action_tuple),[inertia,mistakes]
        # where action tuple looks like: (action_type, amount)
        # self.actions = dict()
        self.instructions = []
        self.possible_actions = set()
        self.generate_possible_actions()
        self.location = np.array([0., 0.])
        self.rotation = 0
        self.speaking = None
        self.logs = dict({
            "food_found": 0,
            "interactions_had": 0,
            "visited_locations": []
        })
        self.role = None
        self.found_food = False

    def generate_possible_actions(self):
        action_type = 0
        for condition_range in self.params["action_types"]:
            for condition in range(*condition_range):
                self.possible_actions.add((action_type, condition))
            action_type += 1

    def is_inertia_higher_then_mistakes(self, input_string):
        inertia, mistakes = self.vocab[input_string][1]
        return inertia > mistakes

    def clear_instructions(self):
        self.instructions = []

    def parse_input(self, input_string: tuple, perform=True):
        if input_string not in list(self.vocab.keys()):
            self.make_random_map(input_string)
        else:
            if not self.is_inertia_higher_then_mistakes(input_string):
                self.make_random_map(input_string)
        if perform:
            self.perform_action(*self.vocab[input_string][0])
        else:
            return self.vocab[input_string][0]

    def perform_action(self, action_type: int, amount: int):
        if action_type == 0:
            self.move(amount)
        elif action_type == 1:
            self.turn(amount * (len(range(*self.params["action_types"][1]))))
        # elif action_type == 2:
        #     self.speak((action_type, amount))
        elif action_type == 2:
            self.speak(amount)

    def move(self, amount: int):
        radians = np.deg2rad(self.rotation)
        c, s = np.cos(radians), np.sin(radians)
        j = np.array([c, s])
        dot = np.dot(j, amount)
        self.location += dot
        self.logs["visited_locations"].append(self.location)

    def turn(self, amount: int):
        self.rotation = (self.rotation + amount) % 360

    def speak(self, topic):
        self.speaking = topic

    def random_walk(self):
        self.turn(random.randint(0, 360))
        self.move(random.randint(0, 4))

    def return_home(self):
        self.location = np.array([0., 0.])
        self.rotation = 0
        self.found_food = False
        self.instructions = []

    def make_random_map(self, input_string: tuple):
        action = random.choice(tuple(self.possible_actions))
        self.set_mapping(input_string, action)
        return action

    def set_mapping(self, input_string: tuple, action: tuple):
        self.vocab[input_string] = [action, [0, 0]]

    def delete_map(self, input_string: tuple):
        del self.vocab[input_string]

    def delete_random_worst_mapping(self):
        worst_mapping_value = 10000
        worst_mappings = []
        for k, v in self.vocab.items():
            inertia = v[1][0]
            if inertia < worst_mapping_value:
                worst_mapping_value = inertia
                worst_mappings = [k]
            elif inertia == worst_mapping_value:
                worst_mappings.append(k)
        mapping_to_delete = random.choice(worst_mappings)
        self.delete_map(mapping_to_delete)

    def reward(self, input_string):
        if input_string not in self.vocab.keys():
            return
        self.vocab[input_string][1][0] += self.params["reward_factor"]
        self.vocab[input_string][1][1] = 0

    def punish(self, input_string):
        if input_string not in self.vocab.keys():
            return
        self.vocab[input_string][1][1] += self.params["punish_factor"]
