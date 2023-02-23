from tdmclient import ClientAsync
import random
import sys
import ttools.movement as tmo


def avoid_objects(node, speed):
    proximity_readout = node.v.prox.horizontal
    left_weights = [0.012, 0.007, -0.0002, -0.0055, -0.011]
    right_weights = [-0.01, -0.005, -0.0001, 0.006, 0.015]
    left = speed
    right = speed
    for i in range(5):
        left += proximity_readout[i] * left_weights[i]
        right += proximity_readout[i] * right_weights[i]
    return left, right


def random_nudge(speed):
    nudge_left = random.randint(-100, 100) / 10
    nudge_right = random.randint(-100, 100) / 10
    left = speed + nudge_left
    right = speed + nudge_right
    return left, right


def generate_motor_targets(left_speed, right_speed):
    return {
        "motor.left.target": [int(left_speed)],
        "motor.right.target": [int(right_speed)],
    }


with ClientAsync() as client:
    async def avoid_and_random_walk():
        runtime = 0
        max_runtime = 1000
        speed = 50
        with await client.lock() as node:
            while runtime <= max_runtime:
                # TODO: test if necessary
                await node.wait_for_variables({"prox.horizontal"})
                if sum(list(node.v.prox.horizontal[:5])) == 0:
                    left_motor_target, right_motor_target = random_nudge(speed)
                else:
                    left_motor_target, right_motor_target = avoid_objects(node, speed)
                # await node.set_variables(motors(left_motor_target, right_motor_target))
                await node.set_variables(tmo.generate_motor_targets(left_motor_target, right_motor_target))
                # node.flush()
                # TODO: test clock speed
                await client.sleep(0.1)
                runtime += 1
            # await node.set_variables(motors(0, 0))
            await node.set_variables(tmo.generate_motor_targets(0, 0))


    client.run_async_program(avoid_and_random_walk)
