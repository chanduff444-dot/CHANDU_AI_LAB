import random
from collections import deque


class SnakeGame:
    """
    Snake environment for RL
    State: 11 binary signals (danger x3, direction x4, food x4)
    Actions: 0=straight  1=turn right  2=turn left
    """

    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        mx, my = self.width // 2, self.height // 2
        self.snake = deque([(mx, my), (mx - 1, my), (mx - 2, my)])
        self.direction = (1, 0)          # start moving right
        self.score = 0
        self.steps = 0
        self.max_steps = self.width * self.height * 3
        self.done = False
        self.food = self._place_food()
        return self._state()

    # ── internals ──────────────────────────────────────────────

    def _place_food(self):
        while True:
            f = (random.randint(0, self.width - 1),
                 random.randint(0, self.height - 1))
            if f not in self.snake:
                return f

    def _is_collision(self, point):
        x, y = point
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return point in self.snake

    def _state(self):
        head = self.snake[0]
        dx, dy = self.direction

        # relative turns
        r_dir = (-dy, dx)    # clockwise right turn
        l_dir = (dy, -dx)    # counter-clockwise left turn

        straight = (head[0] + dx,        head[1] + dy)
        right    = (head[0] + r_dir[0],  head[1] + r_dir[1])
        left     = (head[0] + l_dir[0],  head[1] + l_dir[1])

        return (
            # danger
            self._is_collision(straight),
            self._is_collision(right),
            self._is_collision(left),
            # direction (one-hot)
            dx == -1, dx == 1, dy == -1, dy == 1,
            # food location
            self.food[0] < head[0],   # food is left
            self.food[0] > head[0],   # food is right
            self.food[1] < head[1],   # food is up
            self.food[1] > head[1],   # food is down
        )

    # ── public API ─────────────────────────────────────────────

    def step(self, action):
        if self.done:
            return self._state(), 0, True

        dx, dy = self.direction
        if action == 1:              # turn right
            self.direction = (-dy, dx)
        elif action == 2:            # turn left
            self.direction = (dy, -dx)
        # action == 0 → keep direction

        dx, dy = self.direction
        head = self.snake[0]
        new_head = (head[0] + dx, head[1] + dy)
        self.steps += 1

        if self._is_collision(new_head):
            self.done = True
            return self._state(), -10, True

        self.snake.appendleft(new_head)

        if new_head == self.food:
            self.score += 1
            reward = 10
            self.food = self._place_food()
            self.max_steps = self.width * self.height * 3   # reset after eating
        else:
            self.snake.pop()
            # nudge: closer to food = good, further = bad
            old_d = abs(head[0] - self.food[0]) + abs(head[1] - self.food[1])
            new_d = abs(new_head[0] - self.food[0]) + abs(new_head[1] - self.food[1])
            reward = 1 if new_d < old_d else -1

        if self.steps >= self.max_steps:
            self.done = True
            return self._state(), -10, True

        return self._state(), reward, False

    def render_dict(self):
        snake_list = list(self.snake)
        return {
            "snake":  snake_list,
            "head":   snake_list[0] if snake_list else None,
            "food":   self.food,
            "width":  self.width,
            "height": self.height,
            "score":  self.score,
            "steps":  self.steps,
            "done":   self.done,
        }