class Feature:
    def __init__(self, contents: list, distance_type: list):
        self.contents = []
        self.distance_type = []
        for e_i, element in enumerate(contents):
            self.contents.append(element)
            self.distance_type.append(distance_type[e_i])

    def __str__(self):
        return f"{self.contents}, {self.distance_type}"

    def normalise(self, min_value, max_value):
        factor = 1 / (max_value - min_value)
        for e_i, _ in enumerate(self.contents):
            if self.distance_type[e_i] != bool:
                self.contents[e_i] = self.contents[e_i]*factor

    def have_equal_distance_type(self, other: "Feature"):
        for e_i, element in enumerate(self.distance_type):
            if element != other.distance_type[e_i]:
                return False
        return True

    def squared_distance_with(self, other: "Feature"):
        if not self.have_equal_distance_type(other):
            raise TypeError("features have different distance typing")
        total_sum = 0
        for e_i, _ in enumerate(self.contents):
            if self.distance_type[e_i] == int or self.distance_type[e_i] == float:
                total_sum += (self.contents[e_i] - other.contents[e_i]) ** 2
            if self.distance_type[e_i] == bool:
                total_sum += 0 if self.contents[e_i] == other.contents[e_i] else 1
        return total_sum
