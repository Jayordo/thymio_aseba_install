import ttools.utils as tut
import ttools.movement as tmo
import ttools.basic_behaviours as tbb
import ttools.ir_communication as tic
# import ttools.camera as tca


class Thymio:
    def __init__(self, node):
        self.node = node
        self.hardware_id = self.get_hardware_id()

        # static status values
        # TODO: figure out how to handle status rigidly
        self.timestamp = 0
        self.status = 0
        self.communication_state = 0  # NO_CONTACT
        self.exploring = 1
        self.age = 0
        self.hunger_level = 0
        self.health = 0

        # higher level variables
        self.working_memory = []
        self.add_to_working_memory()
        self.memory = {
            "some_representation_vector": "word"
        }

    def __str__(self):
        return f"{self.hardware_id}"

    def add_to_working_memory(self):
        # add some pruning if memory too full
        self.working_memory.append(
            # for logs/status
            {
                "time_stamp": self.timestamp,
                "status": self.status,
                "exploring": self.exploring,
            }
        )

    # here live main loop functions

    def parse_vision(self):
        # raw_vision = tca.take_picture()

        # TODO: make qr codes and implement basic vision
        raise NotImplementedError

    def enact_behaviour(self):
        # here we decide what happens in a cycle
        # if communication is happening no movement should be happening
        if self.exploring:
            self.explore()

    def explore(self):
        # define exploration loop here
        tbb.avoid_objects(self.node)
        # check for message received
        # check for new items found

    def error_handling(self):
        # parse return codes and resolve problems
        if self.exploring and self.status == "lost":
            raise NotImplementedError

    # here live basic functions

    def stop_moving(self):
        tmo.move(self.node, 0, 0, )

    # here live in class functions

    def get_hardware_id(self):
        # TODO: get hardware id
        return 0
