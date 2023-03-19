import re

from bot import create_from_env
from concurrent.futures import ThreadPoolExecutor

botMap = dict()
botExecutor = ThreadPoolExecutor()

available_game_data_format = ['json']


def createBot():
    botObject = create_from_env()
    botObjectID = botObject.getID()
    botMap.update({botObjectID: botObject})
    return botObjectID


def parse_game_data(botID, data_format: str):
    data_format_map = {
        'json': parse_game_data_to_json,
    }
    data_trans_func = data_format_map.get(data_format)
    raw_data = botMap[botID].getGameData()
    pattern = re.compile(r'<image(((?!(<|>)).)*)></image>')
    pattern_data_list = pattern.findall(raw_data)
    final_data_list = []
    for item in pattern_data_list:
        final_data_list.append(item[0])
    return data_trans_func(final_data_list)


def parse_game_data_to_json(data_list):
    player, enemy, bullet, breakable, impenetrable, other = [] * 6
    typeMap = {
        'BrickWall': breakable,
        'River': impenetrable,
        'steelwall': impenetrable,
        'bullet': bullet,
        'Tank/player': player,
        'Tank/bot': enemy,
        'Forest': other,
        'Snow': other
    }
    result = {}
    Player = {
        'x': 0,
        'y': 0,
        'rotate': 0
    }
    Enemy_List = []
    Bullet_List = []
    for item in enemy:
        Enemy_List.append({'x': 0, 'y': 0, 'rotate': 0})
    result.update({'Player': Player})
    result.update({'Enemy': Enemy_List})
    result.update({'Bullet': Bullet_List})
    result.update({'Breakable': breakable})
    result.update({'Impenetrable ': impenetrable})
    result.update({'Other': other})  # 此项几乎无用，森林/雪地在Bot视角可视为平地
    return result
