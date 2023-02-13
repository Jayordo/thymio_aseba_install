# most basic functions of the Thymio
import random
import time


def generate_motor_targets(left_speed: int, right_speed: int) -> dict:
    return {
        "motor.left.target": [left_speed],
        "motor.right.target": [right_speed],
    }


def move(node, speed_left: int, speed_right: int):
    node.send_set_variables(generate_motor_targets(speed_left, speed_right))


def spin(node, degrees: int, speed_multiplier=1):
    # 500,-500 at sleep 1.14 is roughly enough for a 180
    speed = int(500 * speed_multiplier)
    degree = 0.019 / 3
    # if slower needs longer to reach degree
    seconds = int((degree * degrees)*(1/speed_multiplier))
    move(node, speed, -speed)
    time.sleep(seconds)


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
