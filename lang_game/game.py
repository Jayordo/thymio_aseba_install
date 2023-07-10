from agent import *


class Game:
    def __init__(self, amount_of_agents: int):
        self.robots = []
        self.amount_of_robots = amount_of_agents
        for i in range(amount_of_agents):
            name = f"rob{i}"
            self.robots.append(Agent(name))
        self.image_size = 200
        self.known_images = {}
        self.generate_images(2000)

    def generate_images(self, amount=2000):
        for i in range(amount):
            image = []
            for pixel in range(self.image_size):
                image.append(random.uniform(0, 1))
            self.known_images[f"image{i}"] = image

    def select_two_random_agents(self):
        selected_robots = random.sample(self.robots, 2)
        coinflip = random.randint(0, 1)
        speaker = selected_robots[coinflip]
        listener = selected_robots[not coinflip]
        return speaker, listener

    def play_game_with_two_agents(self, agent1: Agent, agent2: Agent):
        agent1.reset_communication_stats()
        agent2.reset_communication_stats()
        # image = self.generate_random_image(2)
        image = self.select_image_from_known()
        # print(f"\nsent image:{image}")
        agent1.role = "speaker"
        agent1.generate_rep_vec(image)
        initial_token_pair_label = agent1.initial_token_pair_selection()
        agent1.communication_state = "sending"

        agent2.role = "listener"
        agent2.generate_rep_vec(image)
        agent2.parse_received_word_pair(initial_token_pair_label)

        if agent2.communication_state == "agreement":
            agent1.change_token_pair_score_by_label(initial_token_pair_label, "increase")
        elif agent2.communication_state == "disagreement":
            agent1.disagreement_resolution(initial_token_pair_label)
            try:
                agent1.change_token_pair_score_by_label(initial_token_pair_label, "decrease")
            except KeyError:
                raise KeyError("just testing if this happens otherwise remove")
                pass

    def select_image_from_known(self):
        k = random.choice(list(self.known_images.keys()))
        return self.known_images[k]

    @staticmethod
    def generate_random_image(image_size):
        random_image = []
        for i in range(image_size):
            random_image.append(random.uniform(0, 1))
        return random_image
