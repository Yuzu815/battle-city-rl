from bot import create_from_env
from concurrent.futures import ThreadPoolExecutor

botMap = dict()
botExecutor = ThreadPoolExecutor()


def createBot():
    botObject = create_from_env()
    botObjectID = botObject.getID()
    botMap.update({botObjectID: botObject})
    return botObjectID
