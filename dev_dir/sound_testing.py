from tdmclient import ClientAsync
import ttools.utils as tut
import ttools.basic_behaviours as tbb
from thymio import Thymio
import random


#array of 142 samples, with values from -128 to 127
def random_wave():
    wave = []
    for i in range(142):
        wave.append(random.randint(-128,127))
        # wave.append(0)
    aseba_command = f"""
    call sound.wave({wave})
    call sound.freq(800,30)
    """
    return aseba_command


async def end_of_tick_handler(robot: Thymio, sleep_time=0.1, verbose=False):
    # robot.error_handling()  # for example
    if not robot.timestamp % 10 and verbose:
        print(f"runtime: {robot.timestamp}")
    robot.timestamp += 1
    await client.sleep(sleep_time)

with ClientAsync() as client:
    async def main_loop():
        max_runtime = 2
        runtime = 0

        with await client.lock() as node:
            robot = Thymio(node)
            while robot.timestamp <= max_runtime:
                wave = random_wave()
                await node.compile(wave)
                await node.run()
                await end_of_tick_handler(robot,1, verbose=True)
            robot.stop_moving()

    client.run_async_program(main_loop)