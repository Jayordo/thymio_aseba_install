import ttools.movement as tmo
from tdmclient import ClientAsync

with ClientAsync() as client:
    async def basic_loop():
        runtime = 0
        max_runtime = 1000
        with await client.lock() as node:
            while runtime <= max_runtime:
                await client.sleep(0.1)
                runtime += 1
            await node.set_variables(tut.generate_motor_targets(0, 0))


    client.run_async_program(basic_loop)