from tdmclient import ClientAsync
import random

robot107 = "a8755928-f108-4f74-8ef1-133a22a63ce0"
# robot126 =

NO_CONTACT = 0
REQUESTING = 1
INITIATING_CONTACT = 2
START_COUNTING = 3


async def enable_comms(node):
    aseba_command = """
    call prox.comm.enable(1)
    """
    await node.compile(aseba_command)
    await node.run()
    await node.set_variables({"prox.comm.tx": [0]})


def send_message(node, message: int):
    # test values > 1023/2047
    try:
        node.send_set_variables({"prox.comm.tx": [message]})
        return message
    except KeyError:
        # see if this breaks someway?
        send_message(node, message)


def count_up(node, number: int):
    print(f"receiving:{number}")
    return send_message(node, number + 1)


def random_communication_chance(node, communication_state):
    if communication_state == NO_CONTACT and random.random() < 0.01:
        print(f"{node}: searching contact")
        return send_message(node, REQUESTING)
    return NO_CONTACT


def contact_cycle(node, communication_state):
    try:
        received_message = node.v.prox.comm.rx
    # if no received messages gives some chance of starting message requests
    except KeyError:
        return random_communication_chance(node, communication_state)
    if received_message >= START_COUNTING:
        if communication_state >= INITIATING_CONTACT:
            return count_up(node, received_message)

    if received_message == INITIATING_CONTACT:
        if communication_state == REQUESTING:
            return send_message(node, INITIATING_CONTACT)
        if communication_state == INITIATING_CONTACT:
            print("connection successful")
            return send_message(node, START_COUNTING)

    if received_message == REQUESTING:
        print("responding to initiator")
        return send_message(node, INITIATING_CONTACT)
    return random_communication_chance(node, communication_state)


with ClientAsync() as client:
    async def prog():
        communication_state = NO_CONTACT
        runtime = 1000000
        with await client.lock() as node:
            await enable_comms(node)
            while runtime > 0:
                # node.add_variables_changed_listener(on_variables_changed)
                await node.wait_for_variables({"prox.comm.tx"})
                await node.wait_for_variables({"prox.comm.rx"})
                communication_state = contact_cycle(node, communication_state)
                if communication_state >= REQUESTING:
                    client.sleep(1)
                await node.set_variables({"prox.comm.rx": [0]})
                runtime -= 1
                if not runtime % 10:
                    print(runtime)
                # await node.set_variables(tut.generate_motor_targets(0, 0))
                await client.sleep(0.05)
            # await node.unlock()


    client.run_async_program(prog)
