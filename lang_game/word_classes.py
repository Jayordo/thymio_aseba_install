import numpy as np


class RepVec:
    def __init__(self, initial_vector):
        if type(initial_vector) == list:
            self.rep_vec = np.asarray(initial_vector)  # check for size
        elif type(initial_vector) == np.ndarray:
            self.rep_vec = initial_vector
        else:
            raise TypeError(f'initial vector not type list or np array, but of type{type(initial_vector)}')


class ModVec:
    def __init__(self, initial_vector):
        if type(initial_vector) == list:
            self.mod_vec = np.asarray(initial_vector)  # check for size
        elif type(initial_vector) == np.ndarray:
            self.mod_vec = initial_vector
        else:
            raise TypeError(f'initial vector not type list or np array, but of type{type(initial_vector)}')


class Token:
    def __init__(self, label: list, rep_vec: RepVec):
        self.label = label  # check for size
        self.rep_vec = rep_vec.rep_vec

    def __repr__(self):
        return f"label:{self.label} rep_vec: {self.rep_vec}"


class Suffix:
    def __init__(self, label: list, mod_vec: ModVec):
        self.label = label  # check for size
        self.mod_vec = mod_vec.mod_vec

    def __repr__(self):
        return f"label:{self.label} mod_vec: {self.mod_vec}"


class WordPair:
    def __init__(self, token: Token, suffix: Suffix):
        # here be fear of referencial mess
        self.token = token
        self.suffix = suffix
        self.label = token.label + suffix.label
        applied = token.rep_vec + suffix.mod_vec
        clipped = np.clip(applied, 0, 1)
        # TODO: convert to hold multiple rep_vecs
        self.rep_vec = RepVec(clipped).rep_vec

    def __repr__(self):
        return f"label:{self.label} rep_vec: {self.rep_vec}"

    def has_same_label(self, other_word_pair: "WordPair") -> bool:
        return self.label == other_word_pair.label

    def has_same_rep_vec(self, other_word_pair: "WordPair") -> bool:
        return self.rep_vec == other_word_pair.rep_vec
