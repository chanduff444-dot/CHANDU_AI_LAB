import random
import json
import os
from core.game_engine.agents.base_agent import BaseAgent


class QLearningAgent(BaseAgent):
    """
    Tabular Q-Learning Agent
    Works perfectly for GridWorld
    """

    def __init__(
        self,
        n_actions   = 4,
        lr          = 0.1,
        gamma       = 0.95,
        epsilon     = 1.0,
        epsilon_min = 0.05,
        epsilon_decay = 0.995,
    ):
        self.n_actions     = n_actions
        self.lr            = lr
        self.gamma         = gamma
        self.epsilon       = epsilon
        self.epsilon_min   = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table       = {}

    def _get_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * self.n_actions
        return self.q_table[state]

    def select_action(self, state):
        # Explore
        if random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        # Exploit
        q = self._get_q(state)
        return int(q.index(max(q)))

    def update(self, state, action, reward, next_state, done):
        q         = self._get_q(state)
        q_next    = self._get_q(next_state)
        target    = reward + (0 if done else self.gamma * max(q_next))
        q[action] += self.lr * (target - q[action])

    def decay_epsilon(self):
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay
        )

    def save(self, path="data/models/q_table.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(
                {str(k): v for k, v in self.q_table.items()}, f
            )

    def load(self, path="data/models/q_table.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                raw = json.load(f)
                self.q_table = {
                    eval(k): v for k, v in raw.items()
                }