from tdmclient import ClientAsync
import ttools.utils as ttools

with ClientAsync() as client:
    async def prog():
        speed = 100
        running = True
        while running:
            with await client.lock() as node:
                await node.set_variables(ttools.generate_motor_targets(speed, speed))
                await client.sleep(5)
                await node.set_variables(ttools.generate_motor_targets(-speed, -speed))
                await client.sleep(7)
                await node.set_variables(ttools.generate_motor_targets(0, 0))
                running = False
    client.run_async_program(prog)