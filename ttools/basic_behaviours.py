#write some functions that do basic collections of behaviours
#like random walking, grabbing food, eating, following target

#in main loop:
# await node.watch(variables=True)
# node.add_variables_changed_listener(on_variables_changed)

#in function: 
# def on_variables_changed(node, variables):
# send_set_variables(some command) within functions.


def avoid_objects(node, speed):
    proximity_readout = node.v.prox.horizontal
    left_weights = [0.012, 0.007, -0.0002, -0.0055, -0.011]
    right_weights = [-0.01, -0.005, -0.0001, 0.006, 0.015]
    left = speed
    right = speed
    for i in range(5):
        left += proximity_readout[i] * left_weights[i]
        right += proximity_readout[i] * right_weights[i]
    return left, right

