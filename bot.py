import logging
import threading
import time
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from load_env import *


class GameBot:
    game_url = ""
    driver_path = ""
    bot_id = ""
    driver = None
    browser_thread_lock = threading.Lock()

    def __init__(self, game_url, driver_path):
        self.game_url = game_url
        self.driver_path = driver_path
        self.bot_id = str(uuid.uuid4())

    def getID(self):
        return str(self.bot_id)

    def getLockStatus(self):
        if self.browser_thread_lock.locked():
            return False
        return True

    def startBot(self):
        self.browser_thread_lock.acquire()
        self.driver = webdriver.Chrome(self.driver_path)
        self.driver.get(self.game_url)
        current_url = self.driver.current_url
        wait = WebDriverWait(self.driver, 0.1)
        while True:
            try:
                wait.until(expected_conditions.url_changes(current_url))
                current_url = self.driver.current_url
                time.sleep(0.1)
            except TimeoutException:
                logging.info('selenium.current_url未改变，当前请求链接为：{}'.format(current_url))
                if current_url.endswith('gameover'):
                    logging.info('游戏结束，即将重新载入关卡')
                    self.driver.get(self.game_url)
            except NoSuchElementException:
                logging.warning('已脱离游戏状态，无法捕获对应元素')
            except Exception as e:
                logging.error(str(e))
                self.browser_thread_lock.release()
                break

    def send_key(self, key):
        action = ActionChains(self.driver)
        action.key_down(key, element=None)
        action.key_up(key, element=None)
        action.perform()


def create_from_env():
    bot = GameBot(driver_path=BROWSER_DRIVER_PATH, game_url=GAME_URL)
    return bot


if __name__ == '__main__':
    tempBot = create_from_env()
    tempBot.startBot()
