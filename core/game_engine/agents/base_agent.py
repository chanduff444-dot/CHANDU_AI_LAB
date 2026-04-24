class BaseAgent:
    def select_action(self, state):
        raise NotImplementedError

    def update(self, state, action, reward, next_state, done):
        raise NotImplementedError

    def decay_epsilon(self):
        pass