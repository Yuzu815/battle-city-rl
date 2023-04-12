import copy
import random
from datetime import datetime

import gymnasium as gym
import numpy as np
from ray.rllib.env import EnvContext
from utils import create_agent, get_agent_data_by_json, send_command_to_agent, update_canvas


class TankEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array", "human"], "render_fps": 4}

    multiple = 3  # 放大倍数，用于更明显地体现实数坐标的差异
    length = 260  # 游戏默认的画布大小
    uuid = None  # 对应远程环境的uuid
    canvas = None

    _low = 0
    _high = 0

    penalty = 0.1  # 游戏步数的惩罚系数

    level = 1  # 游戏默认值
    HP = 2  # 游戏默认值
    score = 0  # 游戏默认值

    def __init__(self, config: EnvContext):
        super().__init__()
        # 初始化环境
        self._low = 0
        self._high = self.length * self.multiple
        self.observation_space = gym.spaces.Box(low=self._low, high=self._high, shape=(self._high, self._high, 3))
        self.action_space = gym.spaces.Discrete(5)  # 上，下，左，右，开火
        self.obs = 255 * np.ones(shape=[self._high, self._high, 3], dtype=np.uint8)
        self.done = False
        self.render_mode = 'rgb_array'

    def step(self, action):
        map_action = ['w', 'a', 's', 'd', 'j']
        a = datetime.now()
        send_command_to_agent(key=map_action[action], uuid=self.uuid)
        b = datetime.now()
        print((b - a).microseconds)
        reward = self.update()
        obs = self._get_observation()
        return copy.deepcopy(obs), reward, self.done, False, {}

    def reset(self, *, seed=None, options=None):
        random.seed(seed)
        self.uuid = create_agent()
        # 等待远程环境初始化完成
        while True:
            response_dict = self.get_response_dict()
            # print('*** ', response_dict['result'])
            if response_dict['result'] \
                    and ('Player' in response_dict['data']) \
                    and len(response_dict['data']['Player']) > 0:
                break
        self.HP = 2
        self.level = 1
        self.score = 0
        self.update()
        return copy.deepcopy(self._get_observation()), {}

    def get_response_dict(self, sleep_time=None):
        fail_count = 0
        while True:
            try:
                response_dict = get_agent_data_by_json(uuid=self.uuid)
                # print('### ', response_dict['result'])
                if response_dict['result']:
                    self.canvas = update_canvas(response_dict, self.multiple, self._high)
                    break
                elif fail_count > 1000:
                    break
                else:
                    fail_count = fail_count + 1
            except KeyError:
                pass
        return response_dict

    def update(self):
        response_dict = self.get_response_dict()
        if not response_dict['result']:
            self.done = True
            return -5 + (-self.penalty)
        score = response_dict['data']['Score']
        done = response_dict['data']['Done']
        HP = response_dict['data']['HP']
        reward = -self.penalty
        if done:
            reward = reward + (-5)
        if self.score < score:
            reward = reward + ((score - self.score) / 100)
        if HP < self.HP:
            reward = reward + (-2)
            self.HP = HP
        self.done = response_dict['data']['Done']
        return reward

    def _get_observation(self):
        response_dict = self.get_response_dict(sleep_time=0.1)
        if not response_dict['result']:
            self.done = True
            self.canvas = 255 * np.ones(shape=[self._high, self._high, 3], dtype=np.uint8)
        else:
            self.canvas = update_canvas(response_dict, self.multiple, self._high)
            # print("@@@ ", self.uuid, " ", response_dict['result'])
        return self.canvas

    def close(self):
        super().close()

    def render(self):
        return np.transpose(
            self.canvas, axes=(1, 0, 2)
        )
