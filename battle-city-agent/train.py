import os
import time
import gymnasium as gym
import numpy as np

import torch
from tianshou.utils import TensorboardLogger
from torch.utils.tensorboard import SummaryWriter
from tianshou.data import Collector, ReplayBuffer, VectorReplayBuffer
from tianshou.env import SubprocVectorEnv, DummyVectorEnv
from tianshou.policy import DQNPolicy
from tianshou.trainer import offpolicy_trainer
from tianshou.utils.net.common import Net

from utils import create_agent, get_agent_data_by_json, send_command_to_agent, update_canvas


class Tank(gym.Env):
    metadata = {"render_modes": ["rgb_array"], "render_fps": 4}

    multiple = 3  # 放大倍数，用于更明显地体现实数坐标的差异
    length = 260  # 游戏默认的画布大小
    uuid = None  # 对应远程环境的uuid
    canvas = None

    penalty = 5  # 游戏步数的惩罚系数

    level = 1  # 游戏默认值
    HP = 2  # 游戏默认值
    score = 0  # 游戏默认值

    def __init__(self):
        super().__init__()
        # 初始化环境
        _low = 0
        _high = self.length * self.multiple
        self.observation_space = gym.spaces.Box(low=_low, high=_high, shape=(_high, _high, 3))
        self.action_space = gym.spaces.Discrete(5)  # 上，下，左，右，开火
        self.obs = 255 * np.ones(shape=[_high, _high, 3], dtype=np.uint8)
        self.done = False

    def step(self, action):
        map_action = ['w', 'a', 's', 'd', 'j']
        send_command_to_agent(key=map_action[action], uuid=self.uuid)
        reward = self.update()
        obs = self._get_observation()
        return obs, reward, self.done, False, {}

    def reset(self, seed=None, options=None):
        self.uuid = create_agent()
        # 等待远程环境初始化完成
        while True:
            response_dict = get_agent_data_by_json(uuid=self.uuid)
            if response_dict['result'] \
                    and ('Player' in response_dict['data']) \
                    and len(response_dict['data']['Player']) > 0:
                break
            time.sleep(1)
        self.HP = 2
        self.level = 1
        self.score = 0
        self.update()
        return self._get_observation(), {}

    def update(self):
        response_dict = get_agent_data_by_json(uuid=self.uuid)
        update_canvas(response_dict, self.canvas, self.multiple)
        Score = response_dict['data']['Score']
        Done = response_dict['data']['Done']
        HP = response_dict['data']['HP']
        reward = -self.penalty
        if Done:
            reward = reward - 500
        if self.score < Score:
            reward = reward + (Score - self.score)
        if HP < self.HP:
            reward = reward - 200 * (HP - self.HP)
            self.HP = HP
        self.done = response_dict['data']['Done']
        return reward

    def _get_observation(self):
        response_dict = get_agent_data_by_json(uuid=self.uuid)
        update_canvas(response_dict, self.canvas, self.multiple)
        return self.canvas

    def close(self):
        super().close()

    def render(self):
        pass


if __name__ == '__main__':
    pass
