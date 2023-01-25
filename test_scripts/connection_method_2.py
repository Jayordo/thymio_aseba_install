from tdmclient import ClientAsync


def change_top(r, g, b):
    return {f"leds.top": [r, g, b]}


with ClientAsync() as client:
    async def prog():
        with await client.lock() as node:
            await node.set_variables(change_top(0, 0, 32))
            await client.sleep(2)
            await node.set_variables(change_top(32, 0, 0))
    client.run_async_program(prog)
