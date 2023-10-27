class Feature:
    def __init__(self, contents, distance_type):
        self.contents = contents
        self.distance_type = distance_type

    def __str__(self):
        return f"{self.contents}, {self.distance_type}"

    def normalise(self, min_value, max_value):
        factor = 1 / (max_value - min_value)
        if self.distance_type != bool:
            self.contents = self.contents * factor

    def have_equal_distance_type(self, other: "Feature"):
        if self.distance_type != other.distance_type:
            return False
        return True


class FeatureVector:
    def __init__(self):
        self.features = []

    def __iter__(self):
        return iter(self.features)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, item):
        return self.features[item]

    def add_features(self, input_value, input_type, normalize=None):
        try:
            for i, feature_value in enumerate(input_value):
                feature = Feature(feature_value, input_type[i])
                if normalize:
                    feature.normalise(*normalize[i])
                self.features.append(feature)
        except TypeError:
            feature = Feature(input_value, input_type)
            if normalize:
                feature.normalise(*normalize)
            self.features.append(feature)

    def manhattan_distance(self, other_features: "FeatureVector"):
        running_sum = 0
        for i, feature in enumerate(self.features):
            if not feature.have_equal_distance_type(other_features[i]):
                raise TypeError("Features distance types do not match")
            if feature.distance_type == bool:
                running_sum += 0 if feature.contents == other_features[i].contents else 1
            else:
                running_sum += abs(feature.contents - other_features[i].contents)
        return running_sum
