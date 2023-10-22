# from game import random
# from game import np
from game import Game
from agent import Agent
import pandas as pd


class GameAnalysis:
    def __init__(self, imported_game: Game):
        self.game = imported_game

    def print_data(self):
        rows = []
        for rob in self.game.robots:
            rows.append([rob.name, rob.logs["food_found"], rob.logs["interactions_had"]])
        robdf = pd.DataFrame(rows, columns=["name", "food found", "interactions had"]).set_index(["name"])
        return robdf

    @staticmethod
    def vocab_to_df(rob: Agent):
        rows = []
        columns = [f"{rob.name}_input", f"{rob.name}_action",f"{rob.name}_features", f"{rob.name}_inertia", f"{rob.name}_mistakes"]
        for word, action_dict in rob.vocab.items():
            for action, action_data in action_dict.items():
                row = [str(word), str(action), str(action_data[0]), action_data[1][0], action_data[1][1]]
                rows.append(row)
        return pd.DataFrame(rows, columns=columns).set_index([f"{rob.name}_input"])

    def print_vocabs(self):
        for rob in self.game.robots:
            df = self.vocab_to_df(rob)
            if "merged_df" not in locals():
                merged_df = df
            else:
                merged_df = merged_df.join(df, how="outer")
        return merged_df

    def print_vocab_chain(self, requester: Agent, fetcher: Agent):
        dfr = self.vocab_to_df(requester).reset_index()
        dff = self.vocab_to_df(fetcher).reset_index()
        return pd.merge(dfr, dff, left_on="A_action", right_on="B_input", how="outer")

    # def plot_robot_paths(self, l_slice=None, r_slice=None, reverse=True):
    #     fig, ax = plt.subplots()
    #     empty_plot = True
    #     for rob in self.game.robots:
    #         col = (np.random.random(), np.random.random(), np.random.random())
    #         if l_slice and r_slice:
    #             paths_to_plot = rob.logs["taken_paths"][l_slice:r_slice]
    #         elif l_slice or r_slice:
    #             paths_to_plot = rob.logs["taken_paths"][l_slice:]
    #         else:
    #             paths_to_plot = rob.logs["taken_paths"]
    #         if reverse:
    #             paths_to_plot.reverse()
    #         for path in paths_to_plot:
    #             final_location = path[-1]
    #             unzipped = self.unzip_locations(path)
    #             x = unzipped[0]
    #             y = unzipped[1]
    #             # if self.test_for_movement(x, y):
    #             #     empty_plot = False
    #             #     touching_food = False
    #             #     for food_type in self.game.food_types:
    #             #         if self.game.maze.is_player_colliding_with_food(final_location,food_type):
    #             #             touching_food = True
    #             #             print(touching_food)
    #             ax.plot(x, y, c=col)
    #     if not empty_plot:
    #         for food_type in self.game.food_types:
    #             ax.plot(*food_type[1], 'o')
    #             ax.plot(*food_type[1], 'o', markersize=int(self.game.close_enough * 12))
    #         plt.xlim([-self.game.arena_size, self.game.arena_size])
    #         plt.ylim([-self.game.arena_size, self.game.arena_size])
    #         plt.show()
    #     else:
    #         plt.close()

    # @staticmethod
    # def test_for_movement(x, y):
    #     if math.isclose(np.average(x), x[0]) and math.isclose(np.average(y), y[0]):
    #         return False
    #     return True

    def show_instructions(self):
        for rob in self.game.robots:
            if rob.role == "fetcher":
                df = pd.DataFrame(rob.logs["given_sentences"])
                return df

    # @staticmethod
    # def unzip_locations(entries):
    #     x = []
    #     y = []
    #     for entry in entries:
    #         x.append(entry[0])
    #         y.append(entry[1])
    #     return x, y
