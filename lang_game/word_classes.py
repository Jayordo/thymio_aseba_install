import numpy as np

DEFAULT_WORD_SCORE = 1
DEFAULT_SCORE_INCREASE = 1
DEFAULT_SCORE_DECREASE = 0


class Token:
    score: float

    def __init__(self, label: list, initial_vector, score=DEFAULT_WORD_SCORE):
        self.label = label  # check for size
        self.score = score
        if type(initial_vector) == list:
            self.rep_vec = np.asarray(initial_vector)  # check for size
        elif type(initial_vector) == np.ndarray:
            self.rep_vec = initial_vector
        else:
            raise TypeError(f'initial vector not type list or np array, but of type{type(initial_vector)}')

    def __repr__(self):
        return f"label:{self.label} rep_vec: {self.rep_vec}"

    def __lt__(self, other: "Token"):
        return self.score < other.score

    def has_same_label(self, other_token: "Token") -> bool:
        return self.label == other_token.label

    def has_same_rep_vec(self, other_token: "Token") -> bool:
        return self.rep_vec == other_token.rep_vec

    def concat_label(self, other_token: "Token") -> list:
        return self.label + other_token.label

    def combine_rep_vec(self, other_token: "Token") -> np.ndarray:
        # TODO: is this way of combining good, averaging is going to bias towards the centre
        return self.rep_vec + other_token.rep_vec

    def combine_score(self, other_token: "Token") -> float:
        return (self.score + other_token.score) / 2

    def combine_tokens(self, other_token: "Token") -> tuple[list, np.ndarray, float]:
        return self.concat_label(other_token), self.combine_rep_vec(other_token), self.combine_score(other_token)

    def increase_score(self):
        self.score += DEFAULT_SCORE_INCREASE

    def decrease_score(self):
        self.score += DEFAULT_SCORE_DECREASE
