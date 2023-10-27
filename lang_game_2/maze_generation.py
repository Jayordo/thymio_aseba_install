from game import np
from game import random


class MazeGenerator:

    def __init__(self, height, width, difficulty=0):
        self.width = width
        self.height = height
        self.x_left_index = 0
        self.x_right_index = self.width - 1
        self.y_left_index = 0
        self.y_right_index = self.height - 1
        self.grid = np.zeros((width, height), dtype=int)
        self.generate(difficulty)
        self.template = None
        self.generate_template()

    def check_if_not_on_edges(self, x, y):
        return self.x_left_index < x < self.x_right_index and self.y_left_index < y < self.y_right_index

    def frontier(self, x, y):
        # x,y should be between 1 and 8 (with a 10 size grid with indices [0,9]) to be within walls
        # false is a wall
        f = set()
        if self.check_if_not_on_edges(x, y):
            if x > 2 and not self.grid[x - 2][y]:
                f.add((x - 2, y))
            if x + 2 < self.x_right_index and not self.grid[x + 2][y]:
                f.add((x + 2, y))
            if y > 2 and not self.grid[x][y - 2]:
                f.add((x, y - 2))
            if y + 2 < self.y_right_index and not self.grid[x][y + 2]:
                f.add((x, y + 2))
        return f

    def neighbours(self, x, y):
        n = set()
        if self.check_if_not_on_edges(x, y):
            if x > 2 and self.grid[x - 2][y]:
                n.add((x - 2, y))
            if x + 2 < self.x_right_index and self.grid[x + 2][y]:
                n.add((x + 2, y))
            if y > 2 and self.grid[x][y - 2]:
                n.add((x, y - 2))
            if y + 2 < self.y_right_index and self.grid[x][y + 2]:
                n.add((x, y + 2))
        return n

    def connect(self, x1, y1, x2, y2):
        x = (x1 + x2) // 2
        y = (y1 + y2) // 2
        self.grid[x1][y1] = True
        self.grid[x][y] = True

    def generate(self, difficulty=0):
        s = set()
        x, y = (random.randint(self.x_left_index + 1, self.x_right_index - 1),
                random.randint(self.y_left_index + 1, self.y_right_index - 1))
        self.grid[x][y] = True
        fs = self.frontier(x, y)
        for f in fs:
            s.add(f)
        while s:
            x, y = random.choice(tuple(s))
            s.remove((x, y))
            ns = self.neighbours(x, y)
            if ns:
                nx, ny = random.choice(tuple(ns))
                self.connect(x, y, nx, ny)
            fs = self.frontier(x, y)
            for f in fs:
                s.add(f)
        if difficulty > 0:
            for row_i, row in enumerate(self.grid):
                for col_i, cell in enumerate(row):
                    if self.check_if_not_on_edges(row_i, col_i):
                        if not cell:
                            if random.random() > difficulty:
                                self.grid[row_i][col_i] = True

    def generate_template(self):
        self.template = []
        for row in self.grid:
            self.template.append(" ".join(map(str, row)).replace("0", "#").replace("1", "=").replace(" ", ""))

# m = MazeGenerator(15, 15)
# m.add_food()
# m.generate_template()
# pprint.pp(m.template)
