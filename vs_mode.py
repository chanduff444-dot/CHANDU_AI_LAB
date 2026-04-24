"""
vs_mode.py  —  Agent vs Human Snake
Drop this next to your existing files.
"""

import random
from collections import deque


class HumanSnakeGame:
    """
    Separate Snake instance for the human player.
    Direction controlled externally (call set_direction).
    Actions: 0=UP  1=DOWN  2=LEFT  3=RIGHT
    """

    DIR_MAP = {
        0: (0, -1),   # UP
        1: (0,  1),   # DOWN
        2: (-1, 0),   # LEFT
        3: (1,  0),   # RIGHT
    }
    # Prevent 180-degree reversal
    OPPOSITE = {0: 1, 1: 0, 2: 3, 3: 2}

    def __init__(self, width=10, height=10):
        self.width  = width
        self.height = height
        self.reset()

    def reset(self):
        mx, my = self.width // 2, self.height // 2
        # Start moving RIGHT
        self.snake     = deque([(mx, my), (mx - 1, my), (mx - 2, my)])
        self._dir_idx  = 3   # RIGHT
        self.direction = self.DIR_MAP[3]
        self.score     = 0
        self.steps     = 0
        self.done      = False
        self.food      = self._place_food()
        self._pending  = None   # buffered next direction

    def _place_food(self):
        while True:
            f = (random.randint(0, self.width  - 1),
                 random.randint(0, self.height - 1))
            if f not in self.snake:
                return f

    def set_direction(self, action: int):
        """Buffer the next direction (ignores 180° reversal)."""
        if action not in self.DIR_MAP:
            return
        if action == self.OPPOSITE.get(self._dir_idx):
            return   # can't reverse
        self._pending = action

    def step(self):
        if self.done:
            return False

        # Apply buffered direction
        if self._pending is not None:
            self._dir_idx  = self._pending
            self.direction = self.DIR_MAP[self._pending]
            self._pending  = None

        dx, dy    = self.direction
        head      = self.snake[0]
        new_head  = (head[0] + dx, head[1] + dy)
        self.steps += 1

        # Collision check
        x, y = new_head
        if (x < 0 or x >= self.width or
                y < 0 or y >= self.height or
                new_head in self.snake):
            self.done = True
            return False

        self.snake.appendleft(new_head)

        if new_head == self.food:
            self.score += 1
            self.food   = self._place_food()
        else:
            self.snake.pop()

        if self.steps >= self.width * self.height * 5:
            self.done = True
            return False

        return True

    def render_dict(self):
        sl = list(self.snake)
        return {
            "snake":  sl,
            "head":   sl[0] if sl else None,
            "food":   self.food,
            "width":  self.width,
            "height": self.height,
            "score":  self.score,
            "steps":  self.steps,
            "done":   self.done,
        }