from game import random
from game import np
import math


class Agent:
    def __init__(self, name: str, params: dict):
        # given
        self.params = params
        self.name = name
        # inits
        self.vocab = dict()
        self.role = "fetcher"
        self.found_food = False
        self.rotation = 0
        self.current_chain_length = 0

        # This logging stuff needs a rework
        self.current_instructions_received_from = None
        self.current_instructions = []
        self.current_env_features = []
        self.last_subsequent_instructions = []
        self.last_subsequent_env_features = []
        self.last_subsequent_actions = []
        self.last_subsequent_locations = []
        self.logs = dict({
            "food_found": 0,
            "taken_paths": [],
            "given_sentences": []
        })

        # startup functions
        self.possible_actions = self.generate_possible_actions()

    def generate_possible_actions(self):
        action_type = 0
        possible_actions = set()
        for condition_range in self.params["action_types"]:
            for condition in range(*condition_range):
                possible_actions.add((action_type, condition))
            action_type += 1
        return possible_actions

    def is_mistakes_higher_then_inertia(self, given_input: tuple, action: tuple):
        inertia, mistakes = self.vocab[given_input][action][1]
        return mistakes > inertia

    def clear_instructions(self):
        self.current_instructions = []

    def comparison_metrics(self, feature_set: list, other_feature_set: list, method="euclid"):
        if method == "euclid":
            converted_features = other_converted_features = []
            for f_i, feature in enumerate(feature_set):
                if not feature or not other_feature_set[f_i]:
                    continue
                converted_features.append(feature_set[f_i])
                other_converted_features.append(other_feature_set[f_i])
            return self.distance_between_lists(converted_features, other_converted_features)

    @staticmethod
    def distance_between_lists(first_list:list[int], other_list:list[int]):
        subtracted_squares = []
        for l_i, value in enumerate(first_list):
            subtracted_squares.append((value-other_list[l_i])**2)
        return math.sqrt(sum(subtracted_squares))

    def feature_compare(self, given_input: tuple):
        best_metric_low = 10000000000000000
        best_action = None
        for action, action_data in self.vocab[given_input].items():
            known_feature_set = action_data[0]
            metric = self.comparison_metrics(known_feature_set, self.current_env_features, method="euclid")
            if metric < best_metric_low:
                best_metric_low = metric
                best_action = action
        return best_action

    def parse_input(self, given_input: tuple):
        if given_input not in list(self.vocab.keys()):
            self.vocab[given_input] = dict()
            self.make_random_map(given_input)
        action = self.feature_compare(given_input)
        if not action:
            action = self.make_random_map(given_input)
        if self.is_mistakes_higher_then_inertia(given_input, action):
            action = self.make_random_map(given_input)
        # improve together with logging
        self.last_subsequent_env_features.append(self.current_env_features)
        self.last_subsequent_instructions.append(given_input)
        self.last_subsequent_actions.append(action)
        return action

    def reset_to_init(self):
        self.found_food = False
        self.current_chain_length = 0
        self.current_instructions = []
        self.current_env_features = []
        self.current_instructions_received_from = None

    def make_random_map(self, given_input: tuple):
        action = random.choice(tuple(self.possible_actions))
        self.vocab[given_input][action] = [self.current_env_features, [0, 0]]
        return action

    def reward_or_punish(self, given_input: tuple, action: tuple, punish: bool):
        if not punish:
            # increase inertia
            self.vocab[given_input][action][1][0] += self.params["reward_factor"]
            # reset mistakes
            self.vocab[given_input][action][1][1] = 0
        else:
            self.vocab[given_input][action][1][1] += self.params["punish_factor"]

    def write_to_logs(self):
        self.log_instruction_data()
        self.log_locations()
        if self.found_food:
            self.logs["food_found"] += 1

    def log_instruction_data(self):
        if len(self.current_instructions) > 0:
            self.logs["given_sentences"].append(
                [str(self.current_instructions), str(self.last_subsequent_actions), self.found_food])
            self.current_instructions = []
            self.last_subsequent_actions = []
            self.last_subsequent_instructions = []
            self.last_subsequent_env_features = []
            self.current_instructions_received_from = None

    def log_locations(self):
        self.logs["taken_paths"].append(self.last_subsequent_locations)
        self.last_subsequent_locations = []
