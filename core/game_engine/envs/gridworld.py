import numpy as np
import random


class GridWorld:
    """
    Simple 5x5 GridWorld Environment
    - Agent starts at (0,0)
    - Goal at (4,4)
    - Random walls placed
    - Actions: 0=UP 1=DOWN 2=LEFT 3=RIGHT
    """

    def __init__(self, size=5, n_walls=3):
        self.size     = size
        self.n_walls  = n_walls
        self.reset()

    def reset(self):
        self.agent    = [0, 0]
        self.goal     = [self.size - 1, self.size - 1]
        self.walls    = self._place_walls()
        self.done     = False
        self.steps    = 0
        return self._state()

    def _place_walls(self):
        walls = set()
        while len(walls) < self.n_walls:
            w = (
                random.randint(0, self.size - 1),
                random.randint(0, self.size - 1),
            )
            # Don't block start or goal
            if list(w) != self.agent and list(w) != self.goal:
                walls.add(w)
        return walls

    def _state(self):
        return tuple(self.agent)

    def step(self, action):
        if self.done:
            return self._state(), 0, True

        r, c = self.agent
        if action == 0: r -= 1   # UP
        elif action == 1: r += 1  # DOWN
        elif action == 2: c -= 1  # LEFT
        elif action == 3: c += 1  # RIGHT

        # Boundary check
        r = max(0, min(self.size - 1, r))
        c = max(0, min(self.size - 1, c))

        # Wall check
        if (r, c) in self.walls:
            r, c = self.agent  # stay in place

        self.agent = [r, c]
        self.steps += 1

        # Reward
        if self.agent == self.goal:
            self.done = True
            return self._state(), 10.0, True

        if self.steps >= 100:
            self.done = True
            return self._state(), -1.0, True

        return self._state(), -0.1, False

    def render_dict(self):
        """Returns grid as dict for renderer"""
        grid = []
        for r in range(self.size):
            row = []
            for c in range(self.size):
                if [r, c] == self.agent:
                    row.append("agent")
                elif [r, c] == self.goal:
                    row.append("goal")
                elif (r, c) in self.walls:
                    row.append("wall")
                else:
                    row.append("empty")
            grid.append(row)
        return {
            "grid":  grid,
            "size":  self.size,
            "steps": self.steps,
            "done":  self.done,
        }