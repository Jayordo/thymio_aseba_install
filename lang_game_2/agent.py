import random


class Agent:
    def __init__(self, name: str, params: dict):
        self.params = params
        self.name = name
        self.vocab = dict()
        self.speaking = None
        self.instructions = []
        self.last_subsequent_locations = []
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

    def is_mistakes_higher_then_inertia(self, input_string):
        inertia, mistakes = self.vocab[input_string][1]
        return mistakes > inertia

    def clear_instructions(self):
        self.instructions = []

    def parse_input(self, input_string: tuple):
        if input_string not in list(self.vocab.keys()):
            self.make_random_map(input_string)
        else:
            if self.is_mistakes_higher_then_inertia(input_string):
                self.make_random_map(input_string)
        self.last_subsequent_actions.append(self.vocab[input_string][0])
        return self.vocab[input_string][0]

    def generate_sentence(self, starting_topic: tuple, timeout):
        sentence = []
        conversation_topic = self.parse_input(starting_topic)
        sentence.append(conversation_topic)
        while conversation_topic[0] != 2 and timeout > 0:
            conversation_topic = self.parse_input(conversation_topic)
            sentence.append(conversation_topic)
            timeout -= 1
        return sentence

    def reset_and_log(self):
        self.write_to_logs()
        self.found_food = False
        self.rotation = 0

    def make_random_map(self, input_string: tuple):
        action = random.choice(tuple(self.possible_actions))
        self.set_mapping(input_string, action)
        return action

    def set_mapping(self, input_string: tuple, action: tuple):
        self.vocab[input_string] = [action, [0, 0]]

    # def delete_map(self, input_string: tuple):
    #     del self.vocab[input_string]

    # def delete_random_worst_mapping(self):
    #     worst_mapping_value = 10000
    #     worst_mappings = []
    #     for k, v in self.vocab.items():
    #         inertia = v[1][0]
    #         if inertia < worst_mapping_value:
    #             worst_mapping_value = inertia
    #             worst_mappings = [k]
    #         elif inertia == worst_mapping_value:
    #             worst_mappings.append(k)
    #     mapping_to_delete = random.choice(worst_mappings)
    #     self.delete_map(mapping_to_delete)

    def reward(self, input_string):
        if input_string not in self.vocab.keys():
            return
        # increase inertia
        self.vocab[input_string][1][0] += self.params["reward_factor"]
        # reset mistakes
        self.vocab[input_string][1][1] = 0

    def punish(self, input_string):
        if input_string not in self.vocab.keys():
            return
        # increase mistakes
        self.vocab[input_string][1][1] += self.params["punish_factor"]

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

    def log_locations(self):
        self.logs["taken_paths"].append(self.last_subsequent_locations)
        self.last_subsequent_locations = []
