from tdmclient import ClientAsync
import random

with ClientAsync() as client:
    async def prog():
        with await client.lock() as node:
            await node.wait_for_variables({"leds.top"})
            while True:
                for i in [0,1,2]:
                    node.v.leds.top[i] = random.randint(0,32)
                print(list(node.v.leds.top))
                node.flush()
                await client.sleep(0.1)
    client.run_async_program(prog)