import ttools.utils as tut
import ttools.basic_behaviours as tbb
from tdmclient import ClientAsync


def avoid_drop(node, speed):
    floor_proximity = list(node.v.prox.ground.delta)
    # reads between roughly 0(no floor) and 1000(yes floor)
    left_weights = [10**-8, -9**-8]
    right_weights = [-9**-8, 10**-8]
    left = 0
    right = 0
    status = "normal"
    for i, readout in enumerate(floor_proximity):
        readout = int(readout)+1
        # reasonable error
        left += 1/(readout**2 * left_weights[i])
        right += 1/(readout**2 * right_weights[i])
        status = "avoiding"
    return left, right, status


with ClientAsync() as client:
    async def basic_loop():
        runtime = 0
        max_runtime = 1000
        speed = 200
        status = "normal"
        with await client.lock() as node:
            while runtime <= max_runtime:
                await node.wait_for_variables({"prox.ground.delta"})
                left_motor_target, right_motor_target = tbb.avoid_objects(node, speed)
                if sum(list(node.v.prox.ground.delta)) < 1900:
                    print("avoiding")
                    left_motor_target, right_motor_target, status = avoid_drop(node, speed)
                if status == "avoiding":
                    #-100,100 at sleep 5 is roughly enough for a 180
                    await node.set_variables(tut.generate_motor_targets(-speed, speed))
                    await client.sleep(3)
                    status = "normal"
                await node.set_variables(tut.generate_motor_targets(left_motor_target, right_motor_target))
                print(list(node.v.prox.ground.delta))
                print(left_motor_target, right_motor_target)
                await client.sleep(0.1)
                runtime += 1
            await node.set_variables(tut.generate_motor_targets(0, 0))
    client.run_async_program(basic_loop)
