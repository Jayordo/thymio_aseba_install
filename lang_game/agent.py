from word_classes import *
import random


class Agent:

    def __init__(self, name: str):
        self.name = name
        # scores dict where key is word pair and value is score
        self.known_word_pair_scores = {}
        self.known_tokens = []
        self.known_suffixes = []
        self.current_rep_vec = None
        self.role = "neither"
        self.communication_state = "idle"
        self.TOKEN_LENGTH = 5
        self.SUFFIX_LENGTH = 3
        self.SMALLEST_DIFFERENCE = 0.1
        self.DEFAULT_WORD_SCORE = 1
        self.log = {
            "amount_of_interactions": 0,
            "agreed": 0,
            "disagreed": 0,
            "knew_only_token": 0,
            "knew_only_suffix": 0,
            "knew_nothing": 0,
            "no_known_words": 0,
            "words_selected_for_communication": 0,
            "tokens_added": 0,
            "suffixes_added": 0,
            "deleted_tokens": 0,
            "deleted_suffixes": 0,
        }
        self.DEBUG = True

    # Basic functions
    def reset_communication_stats(self):
        self.role = "neither"
        self.communication_state = "idle"
        self.log["amount_of_interactions"] += 1

    # Language game functions
    def generate_rep_vec(self, image: list):  # change later to actually do things
        # TODO: The context of the subject needs to be available too, subject selection can be done in initial word selection. This trickles down into finding agreement on topic.
        image_arr = np.asarray(image)
        if np.any((image_arr < 0)) or np.any((image_arr > 1)):
            raise ValueError('image values not between 0 and 1')
        self.current_rep_vec = image_arr

    def initial_word_pair_selection(self) -> WordPair:
        selected_word_pair = [None, 99999999999999999]
        for word_pair in self.known_word_pair_scores.keys():
            # TODO: rethink if euclidian distance is wanted here. It may be better to select a word with as many features as close as possible excluding entire features first
            euc_dis = self.euclidian_distance(word_pair.rep_vec, self.current_rep_vec)
            # TODO: test score interaction
            # score_multiplier = self.sigmoid(self.known_word_pair_scores[word_pair])
            score_multiplier = max(0.00001,self.known_word_pair_scores[word_pair])
            weighted_distance = euc_dis * score_multiplier
            if weighted_distance < selected_word_pair[1]:  # check for equals
                print(f"{euc_dis}*{score_multiplier}")
                selected_word_pair = [word_pair, weighted_distance]
        if selected_word_pair[0] is None:
            self.randomly_based_word_pair_generation()
            self.log["no_known_words"] += 1
            return self.initial_word_pair_selection()
        # TODO: the now known euclidian distance of the word pair to the current rep_vec may need to play a part in smallest difference
        self.log["words_selected_for_communication"] += 1
        return selected_word_pair[0]

    def parse_received_word_pair(self, received_word_pair_label: list):
        received_token_label, received_suffix_label = self.split_word_pair_label(received_word_pair_label)
        if self.token_label_is_known(received_token_label) and self.suffix_label_is_known(received_suffix_label):
            known_word_pair = self.get_word_pair_by_label(received_word_pair_label)
            # TODO: rethink this, how do they know when there is agreement (maybe there is some amount of agreement)
            if self.euclidian_distance(known_word_pair.rep_vec, self.current_rep_vec) < self.SMALLEST_DIFFERENCE:
                self.communication_state = "agreement"
                self.known_word_pair_scores[known_word_pair] += 1
                self.log["agreed"] += 1
            else:
                self.communication_state = "disagreement"
                self.log["disagreed"] += 1
                # TODO: Make option to average representation or implement possibility of adding multiple
                #  representations to word parts
                # TODO: look for semi-agreement, like agreeing that token + some
                #   unknown/other suffix can lead to this representation
                self.randomly_based_word_pair_generation()
        elif self.token_label_is_known(received_token_label):  # knows only token
            # TODO: implement other options when there are unknowns
            self.log["knew_only_token"] += 1
            known_token = self.get_token_by_label(received_token_label)
            new_suffix = self.create_suffix_through_token_and_suffix_label(received_suffix_label, token=known_token)
            if not self.attempt_addition_of_word_part(suffix=new_suffix):
                raise ValueError("top condition should have succeeded")
        elif self.suffix_label_is_known(received_suffix_label):  # knows only suffix
            self.log["knew_only_suffix"] += 1
            known_suffix = self.get_suffix_by_label(received_suffix_label)
            new_token = self.create_token_through_suffix_and_token_label(received_token_label, suffix=known_suffix)
            if not self.attempt_addition_of_word_part(token=new_token):
                raise ValueError("top condition should have succeeded")
        else:  # no part is known
            self.log["knew_nothing"] += 1
            new_token, new_suffix = self.create_suffix_and_token_through_word_pair_label(received_word_pair_label)
            self.attempt_addition_of_word_part(token=new_token, suffix=new_suffix)
            # TEST compare copying word of speaker vs creating own word
        self.auto_generate_word_pairs()
        return

    # Language functions
    def create_token_through_suffix_and_token_label(self, token_label: list[int], suffix: Suffix) -> Token:
        estimated_rep_vec = RepVec(self.current_rep_vec - suffix.mod_vec)
        return Token(token_label, estimated_rep_vec)

    def create_suffix_through_token_and_suffix_label(self, suffix_label: list[int], token: Token) -> Suffix:
        estimated_mod_vec = ModVec(self.current_rep_vec - token.rep_vec)
        return Suffix(suffix_label, estimated_mod_vec)

    def randomly_based_word_pair_generation(self, base_word_on="neither"):
        if not base_word_on == "neither":
            base_word_on = random.choice(["token", "suffix", "neither"])

        if base_word_on == "token":
            based_on_token = random.choice(self.known_tokens)
            random_suffix_label = self.create_valid_suffix_label()
            new_suffix = self.create_suffix_through_token_and_suffix_label(random_suffix_label, token=based_on_token)
            self.attempt_addition_of_word_part(suffix=new_suffix)

        elif base_word_on == "suffix":
            based_on_suffix = random.choice(self.known_suffixes)
            random_token_label = self.create_valid_token_label()
            new_token = self.create_token_through_suffix_and_token_label(random_token_label, suffix=based_on_suffix)
            self.attempt_addition_of_word_part(token=new_token)

        elif base_word_on == "neither":
            random_token_label = self.create_valid_token_label()
            random_suffix_label = self.create_valid_suffix_label()
            random_word_pair_label = random_token_label + random_suffix_label
            new_token, new_suffix = self.create_suffix_and_token_through_word_pair_label(random_word_pair_label)
            if not self.attempt_addition_of_word_part(token=new_token, suffix=new_suffix):
                raise NotImplementedError("oops")
        self.auto_generate_word_pairs()

    # maybe stick this function into randomly based word generation
    def create_suffix_and_token_through_word_pair_label(self, word_pair_label: list[int], method: str = "random") -> \
            tuple[Token, Suffix]:
        token_label, suffix_label = self.split_word_pair_label(word_pair_label)
        if self.DEBUG:
            if self.token_label_is_known(token_label) or self.suffix_label_is_known(suffix_label):
                raise ValueError("this function can only be used if none of the word parts are known")
        proposed_rep_vec = []
        proposed_mod_vec = []
        if method == "random":
            for feature in self.current_rep_vec:
                random_val = random.uniform(0, 1)
                proposed_rep_vec.append(random_val)
                proposed_mod_vec.append(feature - random_val)
            new_token = Token(token_label, RepVec(proposed_rep_vec))
            new_suffix = Suffix(suffix_label, ModVec(proposed_mod_vec))
        else:
            raise ValueError(f"wordpair creation method {method} not found")
        return new_token, new_suffix

    def attempt_addition_of_word_part(self, token=None, suffix=None, safety_check=True):
        if safety_check:
            if token and suffix:
                if self.token_label_is_known(token.label) or self.suffix_label_is_known(suffix.label):
                    if self.DEBUG: print(f"I already know {token} or {suffix}")
                    return False
            elif token:
                if self.token_label_is_known(token.label):
                    if self.DEBUG: print(f"I already know {token}")
                    return False
            elif suffix:
                if self.suffix_label_is_known(suffix.label):
                    if self.DEBUG: print(f"I already know {suffix}")
                    return False
            else:
                raise ValueError("nothing to add")
        if token:
            self.known_tokens.append(token)
            self.log["tokens_added"] += 1
        if suffix:
            self.known_suffixes.append(suffix)
            self.log["suffixes_added"] += 1
        self.auto_generate_word_pairs()
        return True

    def auto_generate_word_pairs(self):
        for token in self.known_tokens:
            for suffix in self.known_suffixes:
                if not self.word_pair_label_is_known(token.label + suffix.label):
                    word_pair_to_test = WordPair(token, suffix)
                    self.known_word_pair_scores[word_pair_to_test] = self.DEFAULT_WORD_SCORE

    def create_valid_token_label(self) -> list[int]:
        if self.amount_of_token_labels_left() < 1:
            self.prune_worst_known("token")
        return self.recurse_token_name_creation()

    def create_valid_suffix_label(self) -> list[int]:
        if self.amount_of_suffix_labels_left() < 1:
            self.prune_worst_known("suffix")
        return self.recurse_suffix_name_creation()

    def recurse_token_name_creation(self) -> list[int]:
        random_token_label = self.random_bit_list(self.TOKEN_LENGTH)
        if self.token_label_is_known(random_token_label):
            random_token_label = self.recurse_token_name_creation()
        return random_token_label

    def recurse_suffix_name_creation(self) -> list[int]:
        random_suffix_label = self.random_bit_list(self.SUFFIX_LENGTH)
        if self.suffix_label_is_known(random_suffix_label):
            random_suffix_label = self.recurse_suffix_name_creation()
        return random_suffix_label

    def known_token_scores(self):
        token_scores = {}
        for token in self.known_tokens:
            token_scores[token] = 0
            for word_pair in self.known_word_pair_scores.keys():
                if token.label == word_pair.token.label:
                    token_scores[token] += self.known_word_pair_scores[word_pair]
        return token_scores

    def known_suffix_scores(self):
        suffix_scores = {}
        for suffix in self.known_suffixes:
            suffix_scores[suffix] = 0
            for word_pair in self.known_word_pair_scores.keys():
                if suffix.label == word_pair.suffix.label:
                    suffix_scores[suffix] += self.known_word_pair_scores[word_pair]
        return suffix_scores

    def prune_worst_known(self, word_type):
        worst_word = self.find_worst_known(word_type)
        items_to_delete = []
        if word_type == "token":
            for word_pair in self.known_word_pair_scores.keys():
                if word_pair.token == worst_word:
                    items_to_delete.append(word_pair)
            self.log["deleted_tokens"] += 1
            self.known_tokens.remove(worst_word)
        if word_type == "suffix":
            for word_pair in self.known_word_pair_scores.keys():
                if word_pair.suffix == worst_word:
                    items_to_delete.append(word_pair)
            self.log["deleted_suffixes"] += 1
            self.known_suffixes.remove(worst_word)
        for deleted_word_pair in items_to_delete:
            self.known_word_pair_scores.pop(deleted_word_pair)

    def find_worst_known(self, word_type):
        if word_type == "token":
            token_scores = self.known_token_scores()
            lowest_word = min(token_scores, key=token_scores.get)
        elif word_type == "suffix":
            suffix_scores = self.known_suffix_scores()
            lowest_word = min(suffix_scores, key=suffix_scores.get)
        else:
            raise TypeError("word type not token or suffix")
        return lowest_word

    # Fetch functions
    def get_word_pair_by_label(self, word_pair_label: list[int]) -> WordPair:
        for known_word_pair in self.known_word_pair_scores.keys():
            if known_word_pair.label == word_pair_label:
                return known_word_pair
        raise IndexError("word pair not known")

    def get_token_by_label(self, token_label: list[int]) -> Token:
        for known_token in self.known_tokens:
            if known_token.label == token_label:
                return known_token
        raise IndexError("token not known")

    def get_suffix_by_label(self, suffix_label: list[int]) -> Suffix:
        for known_suffix in self.known_suffixes:
            if known_suffix.label == suffix_label:
                return known_suffix
        raise IndexError("suffix not known")

    def split_word_pair_label(self, word_pair_label: list) -> tuple[list[int], list[int]]:
        if len(word_pair_label) != self.TOKEN_LENGTH + self.SUFFIX_LENGTH:
            raise ValueError("word pair label has unexpected length")
        return word_pair_label[:self.TOKEN_LENGTH], word_pair_label[-self.SUFFIX_LENGTH:]

    def token_label_is_known(self, token_label: list[int]) -> bool:
        for known_token in self.known_tokens:
            if known_token.label == token_label:
                return True
        return False

    def suffix_label_is_known(self, suffix_label: list[int]) -> bool:
        for known_suffix in self.known_suffixes:
            if known_suffix.label == suffix_label:
                return True
        return False

    def word_pair_label_is_known(self, word_pair_label: list[int]) -> bool:
        for known_word_pair in self.known_word_pair_scores.keys():
            if known_word_pair.label == word_pair_label:
                return True
        return False

    def amount_of_token_labels_left(self) -> int:
        return 2 ** self.TOKEN_LENGTH - len(self.known_tokens)

    def amount_of_suffix_labels_left(self) -> int:
        return 2 ** self.SUFFIX_LENGTH - len(self.known_suffixes)

    @staticmethod
    def euclidian_distance(point1, point2) -> float:
        return float(np.sum(np.square(point1 - point2)))

    @staticmethod
    def random_bit_list(amount):
        result = []
        for i in range(amount):
            result.append(random.randint(0, 1))
        if len(result) == 1:
            return result[0]
        return result

    # @staticmethod
    def sigmoid(self,x):
        return 1.0 / (1.0 + np.exp(-x))
