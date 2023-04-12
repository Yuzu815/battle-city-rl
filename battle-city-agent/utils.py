import json

import numpy as np
import requests
import cv2
from load_env import MIDDLE_WARE_URL


def update_canvas(dic, mul, length) -> np.array:
    canvas = 255 * np.ones(shape=[length, length, 3], dtype=np.uint8)
    # 河流
    for item in dic['data']['Impenetrable_river']:
        pos_x = int(round(float(item['x']))) * mul
        pos_y = int(round(float(item['y']))) * mul
        cv2.rectangle(canvas, (pos_x, pos_y), (pos_x + 16 * mul, pos_y + 16 * mul), (255, 0, 0), thickness=-1)
    # 普通墙
    for item in dic['data']['Breakable']:
        pos_x = int(round(float(item['x']))) * mul
        pos_y = int(round(float(item['y']))) * mul
        cv2.rectangle(canvas, (pos_x, pos_y), (pos_x + 4 * mul, pos_y + 4 * mul), (0, 255, 0), thickness=-1)
    # 钢铁
    for item in dic['data']['Impenetrable_wall']:
        pos_x = int(round(float(item['x']))) * mul
        pos_y = int(round(float(item['y']))) * mul
        cv2.rectangle(canvas, (pos_x, pos_y), (pos_x + 8 * mul, pos_y + 8 * mul), (0, 0, 255), thickness=-1)
    # 玩家
    for item in dic['data']['Player']:
        pos_x = int(round(float(item['x']))) * mul
        pos_y = int(round(float(item['y']))) * mul
        rotate = int(item['rotate'])
        pos_x, pos_y = trans_tank_position(pos_x, pos_y, 16 * mul, rotate)
        cv2.rectangle(canvas, (pos_x, pos_y), (pos_x + 16 * mul, pos_y + 16 * mul),
                      (rotate % 255, rotate % 255, 100), thickness=-1)
    # 敌人
    for item in dic['data']['Enemy']:
        pos_x = int(round(float(item['x']))) * mul
        pos_y = int(round(float(item['y']))) * mul
        rotate = int(item['rotate'])
        pos_x, pos_y = trans_tank_position(pos_x, pos_y, 16 * mul, rotate)
        cv2.rectangle(canvas, (pos_x, pos_y), (pos_x + 16 * mul, pos_y + 16 * mul),
                      (rotate % 255, rotate % 255, 200), thickness=-1)
    # 子弹
    for item in dic['data']['Bullet']:
        pos_x = int(round(float(item['x']))) * mul
        pos_y = int(round(float(item['y']))) * mul
        cv2.rectangle(canvas, (pos_x, pos_y), (pos_x + 3 * mul, pos_y + 3 * mul), (0, 0, 0), thickness=-1)
    return canvas


def trans_tank_position(pos_x: int, pos_y: int, diff: int, rotate: int) -> (int, int):
    if rotate == -90:
        return pos_x, pos_y - diff
    elif rotate == 0:
        return pos_x, pos_y
    elif rotate == 90:
        return pos_x - diff, pos_y
    else:
        return pos_x - diff, pos_y - diff


def get_agent_data_by_json(uuid) -> dict:
    url = MIDDLE_WARE_URL + '/data/json'
    payload = {'uuid': uuid}
    response = requests.request("GET", url, data=payload)
    response_dict = json.loads(response.text)
    return response_dict


def create_agent():
    createRespond = requests.post(
        url=MIDDLE_WARE_URL + '/create'
    )
    createRespondJson = json.loads(createRespond.text)
    uuid = createRespondJson['data']['uuid']
    try:
        requests.post(
            url=MIDDLE_WARE_URL + '/start',
            data={'uuid': uuid},
            timeout=1  # 中间件暂时没实现异步，采用TimeOut Error特殊处理
        )
    except Exception as e:
        pass
    return uuid


def send_command_to_agent(key, uuid):
    data = requests.post(
        url=MIDDLE_WARE_URL + '/send',
        data={'key': key, 'uuid': uuid}
    )
    return data.text
