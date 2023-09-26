import copy

from agent import *
import matplotlib.pyplot as plt
import pandas as pd


class Game:
    def __init__(self, timeout, amount_of_agents):
        self.timeout = timeout
        self.amount_of_agents = amount_of_agents
        self.arena_size = 20
        self.close_enough = 5
        self.chain_length = 1
        self.max_sentence_length = 3
        self.current_requested_food = None
        self.food_location = None
        self.food_types = []
        self.possible_roles = [
            "requester",
            "fetcher"
        ]
        self.params = dict({
            "action_types": [],
            "reward_factor": 5,
            "punish_factor": 1
        })
        self.prepare_params()
        self.robots = self.generate_robots()
        self.set_food_types(1)

    def set_food_types(self, amount_of_food_types: int):
        food_area = self.arena_size - 10
        for food_type in range(amount_of_food_types):
            food_location = np.array(
                [random.randint(-food_area, food_area), random.randint(-food_area, food_area)])
            self.food_types.append([(food_type,), food_location])

    def prepare_params(self):
        action_buckets = dict({
            "move_buckets": 10,
            "rotation_buckets": 10,
            # "speech_buckets": 10,
            "stop_talking_buckets": 3
        })
        for k, v in action_buckets.items():
            self.params["action_types"].append((0, v))

    def generate_robots(self):
        letter = 65
        robots = []
        for rob_id in range(self.amount_of_agents):
            name = chr(letter + rob_id)
            robots.append(Agent(name, self.params))
        return robots

    def set_new_food(self):
        self.current_requested_food, self.food_location = random.choice(self.food_types)
        # print(self.current_requested_food)
        # print(self.food_location)

    def is_out_of_bounds(self, rob: Agent):
        return abs(rob.location[0]) > self.arena_size or abs(rob.location[1]) > self.arena_size

    def assign_role(self, rob):
        if not self.listen_around(rob):
            rob.role = "requester"
        else:
            rob.role = "fetcher"

    def listen_around(self, rob: Agent):
        used_robs = set()
        while len(used_robs) < len(self.robots):
            rob2 = random.choice(self.robots)
            if rob2 not in used_robs:
                used_robs.add(rob2)
                if rob is not rob2:
                    if rob2.speaking:
                        # if self.distance_to(rob.location, rob2.location) < self.close_enough:
                        return rob2
        return None

    def collect_instructions(self, fetcher: Agent, requester: Agent):
        fetcher.clear_instructions()
        fetcher.instructions.append(requester.speaking)
        conversation_topic = requester.parse_input(requester.speaking, perform=False)
        timeout = self.max_sentence_length
        while conversation_topic[0] != 2 and timeout > 0:
            conversation_topic = requester.parse_input(conversation_topic, perform=False)
            fetcher.instructions.append(conversation_topic)
            timeout -= 1

    def evaluate(self, fetcher: Agent):
        if self.distance_to(fetcher.location, self.food_location) < self.close_enough:
            fetcher.logs["food_found"] += 1
            fetcher.found_food = True
            self.set_new_food()

    @staticmethod
    def reward_or_punish_robs(fetcher: Agent, requester: Agent):
        # reward is true
        for instruction in fetcher.instructions:
            if fetcher.found_food:
                requester.reward(instruction)
                fetcher.reward(instruction)
            else:
                requester.punish(instruction)
                fetcher.punish(instruction)

    def game_loop(self):
        self.set_new_food()
        while self.timeout > 0:
            if self.timeout % 10000 == 0:
                print(self.timeout)
            for rob in self.robots:
                if not rob.role:
                    self.assign_role(rob)
                if rob.role == "requester":
                    self.requesters_turn(rob)
                elif rob.role == "fetcher":
                    self.fetchers_turn(rob)
                else:  # explorer
                    pass
                if self.is_out_of_bounds(rob):
                    rob.return_home()
            self.timeout -= 1

    def requesters_turn(self, requester: Agent):
        requester.speaking = requester.parse_input(self.current_requested_food, perform=False)

    def fetchers_turn(self, fetcher: Agent):
        limit = self.chain_length
        requester = self.listen_around(fetcher)
        if not requester:
            fetcher.role = "requester"
            return
        while limit > 0 and requester and not fetcher.found_food:
            requester = self.listen_around(fetcher)
            self.collect_instructions(fetcher, requester)
            self.execute_multiple_instructions(fetcher)
            limit -= 1
        self.reward_or_punish_robs(fetcher, requester)
        fetcher.return_home()
        return

    def execute_multiple_instructions(self, rob: Agent):
        for instruction in rob.instructions:
            rob.parse_input(instruction)
            self.evaluate(rob)
            if rob.found_food:
                return

    def print_data(self):
        first = True
        for rob in self.robots:
            logs = copy.deepcopy(rob.logs)
            del logs["visited_locations"]
            if first:
                vdf = pd.DataFrame.from_dict(rob.vocab, orient='index',
                                             columns=[f"{rob.name}_action_{rob.role}", "metrics"])
                df2 = pd.DataFrame(vdf['metrics'].tolist(), columns=[f'{rob.name}_inertia', f'{rob.name}_mistakes'],
                                   index=vdf.index)
                vdf = pd.concat([vdf, df2], axis=1)
                vdf = vdf.drop(columns=["metrics"])
                first = False
            else:
                df = pd.DataFrame.from_dict(rob.vocab, orient='index',
                                            columns=[f"{rob.name}_action_{rob.role}", "metrics"])
                df2 = pd.DataFrame(df['metrics'].tolist(), columns=[f'{rob.name}_inertia', f'{rob.name}_mistakes'],
                                   index=df.index)
                df = pd.concat([df, df2], axis=1)
                df = df.drop(columns=["metrics"])
                vdf = vdf.join(df, how="outer")

        robdf = pd.DataFrame(logs, index=[self.robots[0].name])
        for rob in self.robots[1:]:
            tdf = pd.DataFrame(logs, index=[rob.name])
            robdf = pd.concat([robdf, tdf], join="outer")
        return vdf, robdf

    def plot_robot_paths(self, only_last_x=None):
        fig, ax = plt.subplots()
        for rob in self.robots:
            col = (np.random.random(), np.random.random(), np.random.random())
            robot_path = rob.logs["visited_locations"]
            unzipped = self.unzip_locations(robot_path)
            if only_last_x:
                x = unzipped[0][-only_last_x:]
                y = unzipped[1][-only_last_x:]
                ax.plot(x, y, c=col)
            else:
                ax.plot(*unzipped, c=col)
        ax.plot(*self.food_location, 'rp', markersize=14)
        plt.show()

    @staticmethod
    def unzip_locations(entries):
        x = []
        y = []
        for entry in entries:
            x.append(entry[0])
            y.append(entry[1])
        return x, y

    @staticmethod
    def distance_to(point1, point2):
        return abs(np.linalg.norm(point1 - point2))

