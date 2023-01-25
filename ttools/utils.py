#most basic functions of the Thymio
import random


def generate_motor_targets(left_speed, right_speed):
    return {
        "motor.left.target": [int(left_speed)],
        "motor.right.target": [int(right_speed)],
    }


def random_nudge(speed):
    nudge_left = random.randint(-100, 100) / 10
    nudge_right = random.randint(-100, 100) / 10
    left = speed + nudge_left
    right = speed + nudge_right
    return left, right


def avoid_objects(proximity_readout, speed):
    right_weights = [-0.01, -0.005, -0.0001, 0.006, 0.015]
    left_weights = [0.012, 0.007, -0.0002, -0.0055, -0.011]
    left = 0
    right = 0
    for i in range(5):
        left = left + (proximity_readout[i] * left_weights[i])
        right = right + (proximity_readout[i] * right_weights[i])
    right = right + speed
    left = left + speed
    return left, right
