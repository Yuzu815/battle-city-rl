import json

import cv2
import gym
import numpy as np

from utils import create_agent, get_agent_data_by_json, send_command_to_agent, update_canvas


class Tank(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    multiple = 3  # 放大倍数，用于更明显地体现实数坐标的差异
    length = 260  # 游戏默认的画布大小
    uuid = None  # 对应远程环境的uuid
    canvas = None

    def __init__(self):
        super().__init__()
        # 初始化环境
        _low = 0
        _high = self.length * self.multiple
        self.observation_space = gym.spaces.Box(low=_low, high=_high, shape=(_high, _high, 3))
        self.action_space = gym.spaces.Discrete(5)  # 上，下，左，右，开火
        self.canvas = 255 * np.ones(shape=[_high, _high, 3], dtype=np.uint8)
        self.state = None
        self.reward = 0
        self.done = False

    def step(self, action):
        map_action = ['w', 'a', 's', 'd', 'j']
        send_command_to_agent(key=map_action[action], uuid=self.uuid)
        self.update()
        return self.state, self.reward, self.done, {}

    def reset(self, seed=None, options=None):
        self.uuid = create_agent()
        # 等待远程环境初始化完成
        while True:
            response_dict = get_agent_data_by_json(uuid=self.uuid)
            if response_dict['result'] and ('Player' in response_dict['data']) and len(
                    response_dict['data']['Player']) > 0:
                break
        self.update()
        return self.state

    def update(self):
        response_dict = get_agent_data_by_json(uuid=self.uuid)
        update_canvas(response_dict, self.canvas, self.multiple)
        self.state = self.canvas
        self.reward = response_dict['Reward']
        self.done = response_dict['Done']

    def render(self):
        pass


if __name__ == '__main__':
    pass
