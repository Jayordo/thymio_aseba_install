from tdmclient import ClientAsync
import ttools.utils as tut
import ttools.basic_behaviours as tbb
from thymio import Thymio


def end_of_tick_handler(robot: Thymio, sleep_time=0.1, verbose=False):
    robot.error_handling()
    if not robot.timestamp % 10 and verbose:
        print(f"runtime: {robot.timestamp}")
    robot.timestamp += 1
    await client.sleep(sleep_time)


with ClientAsync() as client:
    async def main_loop():
        max_runtime = 1000
        runtime = 0
        with await client.lock() as node:
            robot = Thymio(node)
            while robot.timestamp <= max_runtime:
                # here go timed interactions(10 walk cycles, 1 vision cycle etc.)

                # mb move these inside required functions
                await node.wait_for_variables({"prox.horizontal"})
                robot.enact_behaviour()

                end_of_tick_handler(runtime, verbose=True)
            robot.stop_moving()

    client.run_async_program(main_loop)
