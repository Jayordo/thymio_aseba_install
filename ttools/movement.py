import random
import time


def generate_motor_targets(left_speed: int, right_speed: int) -> dict:
    return {
        "motor.left.target": [left_speed],
        "motor.right.target": [right_speed],
    }


def move(node, speed_left: int, speed_right: int):
    node.send_set_variables(generate_motor_targets(speed_left, speed_right))


def spin(node, degrees: int, speed_multiplier=1, random_mode=False):
    # 500,-500 at sleep 1.14 is roughly enough for a 180
    speed = int(500 * speed_multiplier)
    degree = 0.019 / 3
    # if slower needs longer to reach degree
    # this does not work as flawless as hoped, but good enough
    seconds = int((degree * degrees) * (1 / speed_multiplier))
    if random_mode and random.random() < 0.5:
        speed = -speed
    move(node, speed, -speed)
    time.sleep(seconds)


# unused
def random_nudge(speed):
    nudge_left = random.randint(-100, 100) / 10
    nudge_right = random.randint(-100, 100) / 10
    left = speed + nudge_left
    right = speed + nudge_right
    return left, right
