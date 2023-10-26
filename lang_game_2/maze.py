from maze_generation import MazeGenerator
from game import random
from game import np
import pygame


class Maze:
    def __init__(self, num_of_players: int, arena_size: int, difficulty: float, gui: bool, fps: int):
        # given
        self.num_of_players = num_of_players
        self.arena_size = arena_size
        self.gui = gui
        self.fps = fps
        # empties
        self.gui_turns_to_skip = None
        self.current_requested_food = None
        self.entities = {
            "blocks": dict(),
            "players": dict(),
            "food": dict(),
        }
        self.line_entities = {
            "player_rays": dict()
        }
        # initial functions
        mg = MazeGenerator(self.arena_size, self.arena_size, difficulty)
        self.template = mg.template
        self.player_starting_pos = self.select_random_empty_cell()

        # statics
        self.BLOCK_COLOR = (50, 50, 255)
        self.BG_COLOR = (0, 0, 0)

        # pygame dependent functions
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen, self.unit_size = self.set_screen_size()
        self.player_size = self.unit_size / 4
        self.food_size = self.unit_size / 2
        self.convert_template_to_blocks()

    def select_random_empty_cell(self):
        while True:
            row_i = random.randint(0, len(self.template) - 1)
            row = self.template[row_i]
            cell_i = random.randint(0, len(row) - 1)
            if row[cell_i] == "=":
                return cell_i, row_i

    @staticmethod
    def generate_random_colour():
        return np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)

    def set_screen_size(self):
        if not self.gui:
            return None, 64
        height = pygame.display.Info().current_h * 0.9
        unit_size = int(height / self.arena_size)
        pygame.display.quit()
        screen = pygame.display.set_mode((unit_size * self.arena_size, unit_size * self.arena_size),
                                         flags=pygame.SCALED)
        return screen, unit_size

    def add_food(self, name: tuple):
        x, y = self.select_random_empty_cell()
        while pygame.math.Vector2(x, y).distance_to(self.player_starting_pos) < self.arena_size / 3:
            x, y = self.select_random_empty_cell()
        self.template[y] = self.template[y][:x] + "o" + self.template[y][x + 1:]
        food_object = pygame.Rect((self.unit_size * x, self.unit_size * y, self.food_size, self.food_size))
        self.entities["food"][name] = [self.generate_random_colour(), food_object]

    def add_player(self, name: str):
        col = self.generate_random_colour()
        player = pygame.Rect((
            self.unit_size * self.player_starting_pos[0], self.unit_size * self.player_starting_pos[1],
            self.player_size, self.player_size))
        self.entities["players"][name] = [col, player]
        self.line_entities["player_rays"][name] = [col, player.center, self.calculate_endpoint(player, [0, 0])]

    def convert_template_to_blocks(self):
        for y, line in enumerate(self.template):
            for x, character in enumerate(line):
                if character == "#":
                    name = (x, y)
                    block = pygame.Rect(x * self.unit_size, y * self.unit_size, self.unit_size, self.unit_size)
                    self.entities["blocks"][name] = [self.BLOCK_COLOR, block]

    def is_player_colliding_with_food(self, player_name: str, food_name: tuple):
        player = self.entities["players"][player_name][1]
        food = self.entities["food"][food_name][1]
        return player.colliderect(food)

    def get_player_copy(self, player_name: str):
        return self.entities["players"][player_name][1].copy()

    def check_collision(self, player: pygame.Rect, velocity: float, x_direction: bool):
        for _, block in self.entities["blocks"].values():
            if player.colliderect(block):
                if x_direction:
                    if velocity < 0:
                        player.left = block.right
                    elif velocity > 0:
                        player.right = block.left
                else:
                    if velocity < 0:
                        player.top = block.bottom
                    elif velocity > 0:
                        player.bottom = block.top
                return True
        return False

    def move(self, player_name: str, x_vel: float, y_vel: float):
        player = self.entities["players"][player_name][1]
        player.x += x_vel * self.player_size
        self.check_collision(player, x_vel, True)
        player.y += y_vel * self.player_size
        self.check_collision(player, y_vel, False)
        self.line_entities["player_rays"][player_name][1] = player.center
        self.line_entities["player_rays"][player_name][2] = self.calculate_endpoint(player, [x_vel, y_vel])
        self.calculate_distance_to_forward_block(player_name)
        if self.gui:
            self.clock.tick(self.fps)
            self.show()

    def calculate_distance_to_forward_block(self, player_name: str):
        closest_block_distance = 100000000
        for _, block in self.entities["blocks"].values():
            _, start_pos, end_pos = self.line_entities["player_rays"][player_name]
            clipped_line = block.clipline(start_pos, end_pos)
            if clipped_line:
                distance = pygame.math.Vector2(start_pos).distance_to(clipped_line[0])
                if distance < closest_block_distance:
                    closest_block_distance = distance
                    self.line_entities["player_rays"][player_name][2] = clipped_line[0]
        return closest_block_distance / self.unit_size

    @staticmethod
    def calculate_endpoint(player: pygame.Rect, rotation: [int, int]):
        x, y = rotation
        if x + y == 0:
            x = y = 1
        x = player.center[0] + x * 1000
        y = player.center[1] + y * 1000
        return [x, y]

    def return_to_spawn(self, player_name: str):
        player = self.entities["players"][player_name][1]
        player.x = self.player_starting_pos[0] * self.unit_size
        player.y = self.player_starting_pos[1] * self.unit_size
        self.line_entities["player_rays"][player_name][1] = player.center
        self.line_entities["player_rays"][player_name][2] = self.calculate_endpoint(player, [0, 0])

    def outline_current_food(self):
        current_food = self.entities["food"][self.current_requested_food][1]
        food_outline = pygame.Rect((current_food.x - 2, current_food.y - 2, self.food_size + 4, self.food_size + 4))
        pygame.draw.rect(self.screen, (255, 255, 255), food_outline)

    def show(self):
        if not self.gui:
            return
        self.outline_current_food()
        for entity_type_name, entity_type in self.entities.items():
            for colour, entity in entity_type.values():
                pygame.draw.rect(self.screen, colour, entity)
        for entity_type_name, entity_type in self.line_entities.items():
            for colour, start, end in entity_type.values():
                pygame.draw.line(self.screen, colour, start, end)

        pygame.display.update()
        self.screen.fill(self.BG_COLOR)

    def gui_timer(self):
        if self.gui_turns_to_skip is None:
            pass
        elif self.gui_turns_to_skip > 0:
            self.gui_turns_to_skip -= 1
        else:
            self.gui = True
            self.gui_turns_to_skip = None

    def update_caption(self, elements_to_print: list):
        if self.gui:
            output_string = f""
            for element in elements_to_print:
                output_string += f"{element} "
            output_string += "%"
            pygame.display.set_caption(output_string)

    def keypress_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # this doesnt work with the returning in other random functions
                return True
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == "escape":
                    return True
                if pygame.key.name(event.key) == "right":
                    self.gui_turns_to_skip = 1
                    self.gui = False
                if pygame.key.name(event.key) == "f":
                    self.gui_turns_to_skip = 100
                    self.gui = False
                if pygame.key.name(event.key) == "g":
                    self.gui_turns_to_skip = 1000
                    self.gui = False
                if pygame.key.name(event.key) == "x":
                    self.gui = False
                    pygame.display.set_mode(flags=pygame.HIDDEN)
                    self.gui_turns_to_skip = None
                print(pygame.key.name(event.key))

    @staticmethod
    def kill_pygame():
        pygame.quit()
