import numpy as np
import random
import os
from collections import deque
from core.game_engine.agents.base_agent import BaseAgent


# ── Replay Buffer ──────────────────────────────────────────────────────────

class ReplayBuffer:
    def __init__(self, max_size=10000):
        self.buf = deque(maxlen=max_size)

    def push(self, state, action, reward, next_state, done):
        self.buf.append((
            np.array(state, dtype=np.float32),
            int(action),
            float(reward),
            np.array(next_state, dtype=np.float32),
            float(done),
        ))

    def sample(self, batch_size):
        batch = random.sample(self.buf, batch_size)
        s, a, r, ns, d = zip(*batch)
        return (
            np.array(s),
            np.array(a),
            np.array(r, dtype=np.float32),
            np.array(ns),
            np.array(d, dtype=np.float32),
        )

    def __len__(self):
        return len(self.buf)


# ── Simple Neural Net (numpy only) ────────────────────────────────────────

class SimpleNet:
    """
    3-layer fully-connected net
    input → hidden → hidden → output
    ReLU activations, He initialisation, vanilla SGD
    """

    def __init__(self, input_size, hidden_size, output_size):
        self.W1 = np.random.randn(input_size,  hidden_size)  * np.sqrt(2.0 / input_size)
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, hidden_size)  * np.sqrt(2.0 / hidden_size)
        self.b2 = np.zeros(hidden_size)
        self.W3 = np.random.randn(hidden_size, output_size)  * np.sqrt(2.0 / hidden_size)
        self.b3 = np.zeros(output_size)

    def forward(self, x):
        x = np.array(x, dtype=np.float32)
        self._x0 = x
        self._z1 = x  @ self.W1 + self.b1;  self._a1 = np.maximum(0, self._z1)
        self._z2 = self._a1 @ self.W2 + self.b2;  self._a2 = np.maximum(0, self._z2)
        self._z3 = self._a2 @ self.W3 + self.b3
        return self._z3

    def backward(self, grad_out, lr):
        dW3 = self._a2.T @ grad_out;        db3 = grad_out.sum(0)
        d2  = (grad_out @ self.W3.T) * (self._z2 > 0)
        dW2 = self._a1.T @ d2;             db2 = d2.sum(0)
        d1  = (d2 @ self.W2.T) * (self._z1 > 0)
        dW1 = self._x0.T @ d1;             db1 = d1.sum(0)
        self.W3 -= lr * dW3;  self.b3 -= lr * db3
        self.W2 -= lr * dW2;  self.b2 -= lr * db2
        self.W1 -= lr * dW1;  self.b1 -= lr * db1

    def copy_from(self, other):
        self.W1 = other.W1.copy();  self.b1 = other.b1.copy()
        self.W2 = other.W2.copy();  self.b2 = other.b2.copy()
        self.W3 = other.W3.copy();  self.b3 = other.b3.copy()

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez(path, W1=self.W1, b1=self.b1,
                       W2=self.W2, b2=self.b2,
                       W3=self.W3, b3=self.b3)

    def load(self, path):
        d = np.load(path)
        self.W1 = d["W1"];  self.b1 = d["b1"]
        self.W2 = d["W2"];  self.b2 = d["b2"]
        self.W3 = d["W3"];  self.b3 = d["b3"]


# ── DQN Agent ─────────────────────────────────────────────────────────────

class DQNAgent(BaseAgent):
    """
    Deep Q-Network agent — numpy only, no PyTorch.
    Works with the same 11-signal Snake state as QLearningAgent.
    """

    def __init__(
        self,
        state_size    = 11,
        n_actions     = 3,
        lr            = 0.001,
        gamma         = 0.95,
        epsilon       = 1.0,
        epsilon_min   = 0.05,
        epsilon_decay = 0.995,
        hidden_size   = 256,
        batch_size    = 64,
        target_update = 100,
    ):
        self.n_actions     = n_actions
        self.lr            = lr
        self.gamma         = gamma
        self.epsilon       = epsilon
        self.epsilon_min   = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size    = batch_size
        self.target_update = target_update
        self._steps        = 0

        self.online = SimpleNet(state_size, hidden_size, n_actions)
        self.target = SimpleNet(state_size, hidden_size, n_actions)
        self.target.copy_from(self.online)

        self.memory = ReplayBuffer(10000)

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        q = self.online.forward(np.array(state, dtype=np.float32).reshape(1, -1))
        return int(np.argmax(q[0]))

    def update(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)
        if len(self.memory) < self.batch_size:
            return

        s, a, r, ns, d = self.memory.sample(self.batch_size)

        q_online = self.online.forward(s)           # (B, 3)
        q_next   = self.target.forward(ns)          # (B, 3)
        targets  = r + self.gamma * q_next.max(1) * (1 - d)

        q_target = q_online.copy()
        q_target[np.arange(self.batch_size), a] = targets

        grad = 2.0 * (q_online - q_target) / self.batch_size
        self.online.backward(grad, self.lr)

        self._steps += 1
        if self._steps % self.target_update == 0:
            self.target.copy_from(self.online)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path="data/models/snake_dqn"):
        os.makedirs("data/models", exist_ok=True)
        self.online.save(path)

    def load(self, path="data/models/snake_dqn"):
        npz = path if path.endswith(".npz") else path + ".npz"
        if os.path.exists(npz):
            self.online.load(npz)
            self.target.copy_from(self.online)