import copy
import itertools
from word_classes import *
import random
from typing import Optional


class Agent:
    known_tokens: list[Token]

    def __init__(self, name: str):
        self.TOKEN_LENGTH = 5
        self.SMALLEST_DIFFERENCE = 30
        self.name = name
        self.known_tokens = []
        self.available_labels = self.generate_all_combinations_of_bits(self.TOKEN_LENGTH)
        self.current_rep_vec = None
        self.role = "neither"
        self.communication_state = "idle"

        self.DEBUG = True
        self.log = {
            "amount_of_interactions": 0,
            "agreed": 0,
            "disagreed": 0,
            "knew_only_one_token": 0,
            "knew_nothing": 0,
            "no_known_words": 0,
            "words_selected_for_communication": 0,
            "added_tokens": 0,
            "deleted_tokens": 0,
        }

    # Basic functions
    def reset_communication_stats(self):
        self.role = "neither"
        self.communication_state = "idle"
        self.log["amount_of_interactions"] += 1

    # Language game functions
    def generate_rep_vec(self, image: list):  # change later to actually do things
        image_arr = np.asarray(image)
        image_with_noise = image_arr + np.random.normal(0, 0.01, len(image))
        image_with_noise = np.clip(image_with_noise, 0, 1)
        if np.any((image_with_noise < 0)) or np.any((image_with_noise > 1)):
            raise ValueError('image values not between 0 and 1')
        self.current_rep_vec = image_with_noise

    def initial_token_pair_selection(self) -> list[int]:
        # TODO: how and if to do topic selection
        if len(self.known_tokens) < 1:
            self.log["no_known_words"] += 1
            self.generate_two_random_tokens()
            return self.initial_token_pair_selection()
        selected_tokens = self.known_tokens[0], self.known_tokens[0]
        lowest_weighted_distance = self.calculate_weighted_distance(*selected_tokens)
        for token1 in self.known_tokens:
            for token2 in self.known_tokens:
                weighted_distance = self.calculate_weighted_distance(token1, token2)
                if weighted_distance < lowest_weighted_distance:  # check for equals
                    selected_tokens = token1, token2
                    lowest_weighted_distance = weighted_distance
        self.log["words_selected_for_communication"] += 1
        if lowest_weighted_distance > self.SMALLEST_DIFFERENCE:
            selected_tokens = self.generate_two_random_tokens()
        return selected_tokens[0].concat_label(selected_tokens[1])

    def parse_received_word_pair(self, received_token_pair_label: list[int]):
        token1_label, token2_label = self.split_token_pair_label(received_token_pair_label)
        token1_is_known = self.token_label_is_known(token1_label)
        token2_is_known = self.token_label_is_known(token2_label)
        if token1_is_known and token2_is_known:
            [known_token1, known_token2] = self.get_tokens_by_label([token1_label, token2_label])
            # TODO: rethink this, how do they know when there is agreement (maybe there is some amount of agreement)
            combined_rep_vec = known_token1.combine_rep_vec(known_token2)
            # TODO: euclidian distance on shorter vectors? halp
            if self.euclidian_distance(combined_rep_vec, self.current_rep_vec) < self.SMALLEST_DIFFERENCE:
                self.communication_state = "agreement"
                known_token1.increase_score()
                known_token2.increase_score()
                self.log["agreed"] += 1
            else:
                self.communication_state = "disagreement"
                self.log["disagreed"] += 1
                self.disagreement_resolution(received_token_pair_label)
                # TODO: look for semi-agreement, like agreeing that token + some
                #   unknown/other suffix can lead to this representation
        elif token1_is_known or token2_is_known:
            if token1_is_known:
                known_token = self.get_token_by_label(token1_label)
                unknown_token_label = token2_label
            else:
                known_token = self.get_token_by_label(token2_label)
                unknown_token_label = token1_label
            self.log["knew_only_one_token"] += 1
            self.new_token_generation(known_token, unknown_token_label)
        else:
            self.log["knew_nothing"] += 1
            self.generate_two_random_tokens(received_token_pair_label)
        return

    def disagreement_resolution(self, token_pair_label: list[int]):
        tokens = self.get_tokens_by_label(list(self.split_token_pair_label(token_pair_label)))
        # TODO: probs test this
        tokens.sort()
        intermediate_representation = self.current_rep_vec - tokens[0].rep_vec
        rep_vec_copy = copy.deepcopy(tokens[1].rep_vec)
        tokens[1].rep_vec = (tokens[1].rep_vec + intermediate_representation) / 2
        for counter in range(len(tokens[1].rep_vec)):
            if rep_vec_copy[counter] == 0:
                tokens[1].rep_vec[counter] = 0

    def calculate_weighted_distance(self, token1, token2):
        combined_label, combined_rep_vec, combined_score = token1.combine_tokens(token2)
        euc_dis = self.euclidian_distance(combined_rep_vec, self.current_rep_vec)
        # TODO: test multiple ways of implementing score interaction
        score_multiplier = self.sigmoid(combined_score)
        # score_multiplier = max(0.00001, combined_score)
        return euc_dis / score_multiplier

    def change_token_pair_score_by_label(self, token_pair_label: list[int], direction: str):
        tokens = self.get_tokens_by_label(list(self.split_token_pair_label(token_pair_label)))
        for token in tokens:
            if direction == "increase":
                token.increase_score()
            else:
                token.decrease_score()

    # Language functions

    def new_token_generation(self, base_word_on: Optional[Token] = None,
                             new_label: Optional[list[int]] = None) -> Token:
        if base_word_on:
            new_rep_vec = self.current_rep_vec - base_word_on.rep_vec
        else:
            new_rep_vec = self.random_uniform_list(len(self.current_rep_vec))
        if not new_label:
            new_label = self.generate_new_label()
        else:
            self.available_labels.remove(new_label)
        if self.token_label_is_known(new_label):
            if len(self.available_labels) < 1:
                raise RuntimeError("available labels empty")
            else:
                known_token = self.get_token_by_label(new_label)
                print(self.available_labels)
                raise RuntimeError(f"new label {new_label} is the same as known label {known_token}")
        new_token = Token(new_label, new_rep_vec)
        self.topic_creation(new_token)
        self.log["added_tokens"] += 1
        self.known_tokens.append(new_token)
        return new_token

    def generate_two_random_tokens(self, token_pair_label=None):
        if token_pair_label:
            label1, label2 = self.split_token_pair_label(token_pair_label)
            if label1 == label2:
                return self.double_token_label_handler(label1)
        else:
            label1 = None
            label2 = None
        token1 = self.new_token_generation(new_label=label1)
        token2 = self.new_token_generation(token1, new_label=label2)
        return token1, token2

    def double_token_label_handler(self, token_label):
        new_rep_vec = self.current_rep_vec / 2
        new_token = Token(token_label, new_rep_vec)
        self.log["added_tokens"] += 1
        self.known_tokens.append(new_token)
        return new_token, new_token

    def generate_new_label(self):
        if len(self.available_labels) < 1:
            self.delete_worst_token()
        ind = random.randrange(len(self.available_labels))
        return self.available_labels.pop(ind)

    def delete_worst_token(self):
        worst_token = self.known_tokens[0]
        for token in self.known_tokens[1:]:
            if token.score < worst_token.score:
                worst_token = token
        self.log["deleted_tokens"] += 1
        self.available_labels.append(worst_token.label)
        self.known_tokens.remove(worst_token)

    # Fetch functions

    def split_token_pair_label(self, token_pair_label: list[int]) -> tuple[list[int], list[int]]:
        return token_pair_label[:self.TOKEN_LENGTH], token_pair_label[self.TOKEN_LENGTH:]

    def token_label_is_known(self, token_label: list[int]) -> bool:
        for known_token in self.known_tokens:
            if known_token.label == token_label:
                return True
        return False

    def get_tokens_by_label(self, token_labels: list[list[int]]) -> list[Token]:
        fetched_tokens = []
        for token_label in token_labels:
            found = False
            for known_token in self.known_tokens:
                if known_token.label == token_label:
                    found = True
                    fetched_tokens.append(known_token)
                    break
            if not found:
                raise IndexError("token not known")
        return fetched_tokens

    def get_token_by_label(self, token_label: list[int]) -> Token:
        return self.get_tokens_by_label([token_label])[0]

    def topic_creation(self, token: Token):
        amount_to_remove = random.randint(0, len(token.rep_vec))
        indexes = np.random.choice(range(len(token.rep_vec)), size=amount_to_remove, replace=False)
        for i in indexes:
            token.rep_vec[i] = 0

    @staticmethod
    def euclidian_distance(point1, point2) -> float:
        return float(np.sum(np.square(point1 - point2)))

    @staticmethod
    def random_bit_list(amount: int) -> list[int]:
        result = []
        for i in range(amount):
            result.append(random.randint(0, 1))
        if len(result) == 1:
            return result[0]
        return result

    @staticmethod
    def random_uniform_list(amount: int) -> list[float]:
        result = []
        for i in range(amount):
            # TODO: is -1 good here? otherwise everything is going to average to the centre
            result.append(random.uniform(-1, 1))
        return result

    @staticmethod
    def sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))

    @staticmethod
    def generate_all_combinations_of_bits(length):
        return list(itertools.product([0, 1], repeat=length))
