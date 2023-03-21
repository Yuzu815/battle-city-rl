from flask import request, Blueprint
from utils import botMap, createBot, available_game_data_format, parse_game_data

opt = Blueprint('opt', __name__)


@opt.route('/')
def hello():
    return {'result': True, 'data': 'Hello World!'}


@opt.route('/create', methods=['POST'])
def create():
    try:
        botObjectID = createBot()
    except Exception as e:
        return {'result': False, 'message': str(e)}
    return {'result': True, 'data': {'uuid': botObjectID}}


@opt.route('/start', methods=['POST'])
def start():
    try:
        botID = request.form['uuid']
        botObject = botMap[botID]
        if not botObject.getLockStatus():
            return {'result': False, 'message': 'Locked'}
        botObject.startBot()
    except KeyError:
        return {'result': False, 'message': 'KeyError: The bot does not exist or the UUID field does not exist.'}
    except Exception as e:
        return {'result': False, 'message': str(e)}
    return {'result': True}


@opt.route('/list', methods=['GET'])
def list_bots():
    try:
        idList = list(botMap.keys())
    except Exception as e:
        return {'result': False, 'message': str(e)}
    return {'result': True, 'data': idList}


@opt.route('/data/<string:data_format>', methods=['GET'])
def get_game_data(data_format):
    try:
        if data_format not in available_game_data_format:
            raise ValueError('Can\'t support {}'.format(data_format))
        botID = request.form['uuid']
        result = parse_game_data(botID, data_format)
    except KeyError:
        return {'result': False, 'message': 'KeyError: The bot does not exist or the UUID field does not exist.'}
    except Exception as e:
        return {'result': False, 'message': str(e)}
    return {'result': True, 'data': result}


@opt.route('/send', methods=['POST'])
def send_operate_key():
    try:
        key = request.form['key']
        botID = request.form['uuid']
        if key not in ['w', 'a', 's', 'd', 'j']:
            raise KeyError("Invalid Key!")
        botObject = botMap[botID]
        botObject.send_key(key)
    except KeyError:
        return {'result': False, 'message': 'KeyError: The bot does not exist or the UUID field does not exist.'}
    except Exception as e:
        return {'result': False, 'message': str(e)}
    return {'result': True}
