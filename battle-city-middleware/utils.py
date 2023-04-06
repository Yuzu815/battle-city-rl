import re

from bot import create_from_env
from concurrent.futures import ThreadPoolExecutor

from init_variable import duplicate

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
    bot_status = botMap[botID].returnGameStatus()
    pattern = re.compile(r'<image(((?!(<|>)).)*)></image>')
    pattern_data_list = pattern.findall(raw_data)
    pattern_bullet = re.compile(r'<g class="bullet" transform="translate[^<>]*>'
                                r'<rect[^<>]*>[^<>]*</rect>'
                                r'<rect[^<>]*>[^<>]*</rect></g>')
    pattern_bullet_data_list = pattern_bullet.findall(raw_data)
    final_data_list = []
    for item in pattern_data_list:
        final_data_list.append(item[0])
    for item_bullet in pattern_bullet_data_list:
        final_data_list.append(item_bullet)
    return data_trans_func(final_data_list, bot_status)


def parse_game_data_to_json(data_list, game_status):
    player, enemy, bullet, breakable, impenetrable_wall, impenetrable_river, other = duplicate([], 7)
    typeMap = {
        'BrickWall': breakable,
        'River': impenetrable_river,
        'steelwall': impenetrable_wall,
        'bullet': bullet,
        'Tank/player': player,
        'Tank/bot': enemy,
        'Forest': other,
        'Snow': other
    }
    for item in data_list:
        for key, value in typeMap.items():
            if key in item:
                position_pattern = r'translate\([-+]?\d+(\.\d+)?,\s*([-+]?\d+(\.\d+)?)\)'
                rotate_pattern = r'rotate\([-+]?\d+(\.\d+)?\)'
                position_match = re.search(position_pattern, item)
                rotate_match = re.search(rotate_pattern, item)
                result = {}
                if position_match:
                    number_list = get_number_list(str(position_match.group()))
                    x, y = number_list[0], number_list[1]
                    result.update({'x': x, 'y': y})
                if rotate_match:
                    number_list = get_number_list(str(rotate_match.group()))
                    rotate = number_list[0]
                    result.update({'rotate': rotate})
                if result:
                    value.append(result)
    result = {}
    result.update({'Player': player})
    result.update({'Enemy': enemy})
    result.update({'Bullet': bullet})
    result.update({'Breakable': breakable})
    result.update({'Impenetrable_wall': impenetrable_wall})
    result.update({'Impenetrable_river': impenetrable_river})
    result.update({'Other': other})  # 此项几乎无用，森林/雪地在Bot视角可视为平地
    result.update({'Done': game_status['done']})
    result.update({'HP': game_status['HP']})
    result.update({'Score': game_status['score']})
    result.update({'Level': game_status['level']})
    return result


def get_number_list(s):
    pattern = r'[-+]?\d+(?:\.\d+)?'
    result = re.findall(pattern, s)
    return result
