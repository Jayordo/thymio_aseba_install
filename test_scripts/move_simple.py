from tdmclient import ClientAsync
import random

def motors(left, right):
    return {
        "motor.left.target": [left],
        "motor.right.target": [right],
    }


def change_top(r, g, b):
    return {f"leds.top": [r, g, b]}


def on_variables_changed(node, variables):
    try:
        prox = variables["prox.horizontal"]
        prox_front = prox[2]
        speed = -prox_front // 10
        node.send_set_variables(motors(speed, speed))
    except KeyError:
        pass  # prox.horizontal not found


with ClientAsync() as client:
    async def prog():
        with await client.lock() as node:
            await node.wait_for_variables({"leds.top"})
            while True:
                for colour in node.v.leds.top:
                    colour = random.randint(0,32)
                print(node.v.leds.top)
                node.flush()
                await client.sleep(0.01)
            # await node.set_variables(change_top(0, 0, 32))
            # await client.sleep(2)
            # await node.set_variables(change_top(32, 0, 0))


    client.run_async_program(prog)
