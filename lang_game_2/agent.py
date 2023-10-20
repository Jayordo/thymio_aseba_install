import random

import numpy as np


class Agent:
    def __init__(self, name: str, params: dict):
        self.params = params
        self.name = name
        self.vocab = dict()
        # self.action_vocab = dict()
        self.speaking = None
        self.instructions = []
        self.instructions_received_from = None
        self.last_subsequent_locations = []
        self.last_subsequent_instructions = []
        self.last_subsequent_env_features = []
        self.last_subsequent_actions = []
        self.possible_actions = self.generate_possible_actions()
        self.logs = dict({
            "food_found": 0,
            "interactions_had": 0,
            "taken_paths": [],
            "given_sentences": []
        })
        self.role = None
        self.found_food = False
        self.rotation = 0

    def generate_possible_actions(self):
        action_type = 0
        possible_actions = set()
        for condition_range in self.params["action_types"]:
            for condition in range(*condition_range):
                possible_actions.add((action_type, condition))
            action_type += 1
        return possible_actions

    def is_mistakes_higher_then_inertia(self, given_input, action):
        inertia, mistakes = self.vocab[given_input][action][1]
        return mistakes > inertia

    def clear_instructions(self):
        self.instructions = []

    def comparison_metrics(self, feature_set: list, other_feature_set: list, method="euclid"):
        if method == "euclid":
            converted_features = []
            other_converted_features = []
            for f_i, feature in enumerate(feature_set):
                if type(feature) is not tuple:
                    normalised_feature,other_normalised_feature = self.normalise_to_bool(feature_set[f_i],other_feature_set[f_i])
                    converted_features.append(normalised_feature)
                    other_converted_features.append(other_normalised_feature)
                else:
                    converted_features.append(feature_set[f_i])
                    other_converted_features.append(other_feature_set[f_i])
            return abs(np.linalg.norm(np.array(converted_features) - np.array(other_converted_features)))

    @staticmethod
    def normalise_to_bool(expression, other_expression):
        if expression == other_expression:
            return (0, 0), (0, 0)
        else:
            return (0, 0), (0, 1)

    def feature_compare(self, given_input: tuple, env_features: list):
        best_metric_low = 100000
        best_action = None
        for action, action_data in self.vocab[given_input].items():
            known_feature_set = action_data[0]
            metric = self.comparison_metrics(known_feature_set, env_features, method="euclid")
            if metric < best_metric_low:
                best_metric_low = metric
                best_action = action
        return best_action

    def parse_input(self, given_input: tuple, env_features: list):
        if given_input not in list(self.vocab.keys()):
            self.vocab[given_input] = dict()
            self.make_random_map(given_input, env_features)
        action = self.feature_compare(given_input, env_features)
        if self.is_mistakes_higher_then_inertia(given_input, action):
            self.make_random_map(given_input, env_features)
            action = self.feature_compare(given_input, env_features)
        self.last_subsequent_env_features.append(env_features)
        self.last_subsequent_instructions.append(given_input)
        self.last_subsequent_actions.append(action)
        return action

    def generate_sentence(self, starting_topic: tuple, timeout, env_features):
        sentence = []
        conversation_topic = self.parse_input(starting_topic, env_features)
        sentence.append(conversation_topic)
        while conversation_topic[0] != 2 and timeout > 0:
            conversation_topic = self.parse_input(conversation_topic, env_features)
            sentence.append(conversation_topic)
            timeout -= 1
        return sentence

    def reset_and_log(self):
        self.write_to_logs()
        self.found_food = False
        self.rotation = 0

    def make_random_map(self, given_input: tuple, env_features: list):
        action = random.choice(tuple(self.possible_actions))
        self.vocab[given_input][action] = [env_features, [0, 0]]
        return action

    def reward_or_punish(self, given_input,action, punish):
        # if given_input not in self.vocab.keys():
        #     return
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
        if len(self.instructions) > 0:
            self.logs["given_sentences"].append(
                [str(self.instructions), str(self.last_subsequent_actions), self.found_food])
            self.instructions = []
            self.last_subsequent_actions = []
            self.last_subsequent_instructions = []
            self.instructions_received_from = None

    def log_locations(self):
        self.logs["taken_paths"].append(self.last_subsequent_locations)
        self.last_subsequent_locations = []
