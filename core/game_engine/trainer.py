import os
from core.game_engine.envs.snake import SnakeGame
from core.game_engine.agents.q_learning import QLearningAgent
from core.game_engine.agents.dqn_agent import DQNAgent


def _make_agent(algorithm, lr, gamma, epsilon, epsilon_decay):
    if algorithm == "dqn":
        return DQNAgent(
            state_size=11, n_actions=3,
            lr=lr, gamma=gamma,
            epsilon=epsilon, epsilon_decay=epsilon_decay,
        )
    return QLearningAgent(
        n_actions=3, lr=lr, gamma=gamma,
        epsilon=epsilon, epsilon_decay=epsilon_decay,
    )


def _save_path(algorithm):
    return "data/models/snake_dqn" if algorithm == "dqn" else "data/models/snake_q_table.json"


def train_snake_live(
    episodes      = 500,
    width         = 10,
    height        = 10,
    lr            = 0.1,
    gamma         = 0.95,
    epsilon       = 1.0,
    epsilon_decay = 0.995,
    algorithm     = "qlearning",
):
    """Generator — yields one frame dict per step. Final frame has training_complete=True."""
    env   = SnakeGame(width=width, height=height)
    agent = _make_agent(algorithm, lr, gamma, epsilon, epsilon_decay)
    rewards = []

    for ep in range(episodes):
        state        = env.reset()
        total_reward = 0

        while True:
            frame = env.render_dict()
            frame.update({
                "episode":           ep,
                "total_episodes":    episodes,
                "epsilon":           round(agent.epsilon, 3),
                "total_reward":      round(total_reward, 1),
                "rewards_so_far":    list(rewards),
                "training_complete": False,
                "algorithm":         algorithm,
            })
            yield frame

            action                   = agent.select_action(state)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state        = next_state
            total_reward += reward

            if done:
                break

        rewards.append(total_reward)
        agent.decay_epsilon()

    agent.save(_save_path(algorithm))

    final = env.render_dict()
    final.update({
        "episode":           episodes - 1,
        "total_episodes":    episodes,
        "epsilon":           round(agent.epsilon, 3),
        "total_reward":      round(rewards[-1], 1),
        "rewards_so_far":    rewards,
        "best_score":        max(rewards),
        "training_complete": True,
        "algorithm":         algorithm,
    })
    yield final


def replay_trained_agent(
    width     = 10,
    height    = 10,
    episodes  = 5,
    algorithm = "qlearning",
):
    """Load saved model, watch it play — no training, epsilon=0."""
    path = _save_path(algorithm)

    exists = (
        os.path.exists(path + ".npz")
        if algorithm == "dqn"
        else os.path.exists(path)
    )
    if not exists:
        yield {"error": f"No saved model found. Train the agent first."}
        return

    if algorithm == "dqn":
        agent = DQNAgent(state_size=11, n_actions=3, epsilon=0.0)
        agent.load(path)
    else:
        agent = QLearningAgent(n_actions=3, epsilon=0.0)
        agent.load(path)

    env = SnakeGame(width=width, height=height)

    for ep in range(episodes):
        state = env.reset()
        while True:
            frame = env.render_dict()
            frame.update({"episode": ep, "total_episodes": episodes, "replay": True})
            yield frame

            action         = agent.select_action(state)
            state, _, done = env.step(action)

            if done:
                frame = env.render_dict()
                frame.update({"episode": ep, "total_episodes": episodes, "replay": True})
                yield frame
                break