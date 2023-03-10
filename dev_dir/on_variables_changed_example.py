from tdmclient import ClientAsync


def motors(left, right):
    return {
        "motor.left.target": [left],
        "motor.right.target": [right],
    }


def on_variables_changed(node, variables):
    try:
        prox = variables["prox.horizontal"]
        prox_front = prox[2]
        speed = -prox_front // 10
        node.send_set_variables(motors(speed, speed))
    except KeyError:
        pass  # prox.horizontal not found


def on_variables_changed_2(node, variables):
    try:
        print(variables)
        prox = variables["prox.horizontal"]
        prox_side = prox[0]
        if prox_side > 100:
            node.send_set_variables({"leds.top": [0, 32, 32]})
        else:
            node.send_set_variables({"leds.top": [0, 0, 32]})
    except KeyError:
        pass  # prox.horizontal not found


with ClientAsync() as client:
    async def prog():
        with await client.lock() as node:
            await node.watch(variables=True)
            node.add_variables_changed_listener(on_variables_changed)
            node.add_variables_changed_listener(on_variables_changed_2)
            await client.sleep()
    client.run_async_program(prog)
