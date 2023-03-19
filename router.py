import _thread
from flask import request, Blueprint

from bot import GameBot
from utils import botMap, createBot, botExecutor

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


@opt.route('/send', methods=['POST'])
def send_operate_key():
    try:
        key = request.form['key']
        botID = request.form['uuid']
        if key not in ['w', 'a', 's', 'd', 'j']:
            raise KeyError("Invalid Key!")
        botObject = botMap[botID]
        botObject.send_key(key)
    except Exception as e:
        return {'result': False, 'message': str(e)}
    return {'result': True}
