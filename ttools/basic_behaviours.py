# write some functions that do basic collections of behaviours
# like random walking, grabbing food, eating, following target

# in main loop:
# await node.watch(variables=True)
# node.add_variables_changed_listener(on_variables_changed)

# in function:
# def on_variables_changed(node, variables):
# send_set_variables(some command) within functions.

import ttools.utils as tut
import ttools.movement as tmo


def avoid_objects(node, speed=100, sensitivity=6):
    # speed between -500 and 500
    # sensitivity 6 on speed 100 seems to work out with the usb cables
    proximity_readout = node.v.prox.horizontal
    left = right = speed

    # took these froooooom source?
    left_weights = tut.scalar_multiply_list([0.012, 0.007, -0.0002, -0.0055, -0.011], sensitivity)
    right_weights = tut.scalar_multiply_list([-0.01, -0.005, -0.0001, 0.006, 0.015], sensitivity)

    for i in range(5):
        readout = proximity_readout[i]
        # when really close to a wall do a 180
        if readout > 3700:
            tmo.spin(node, 120, 0.5, True)
            return
        left += readout * left_weights[i]
        right += readout * right_weights[i]
    tmo.move(node, int(left), int(right))
