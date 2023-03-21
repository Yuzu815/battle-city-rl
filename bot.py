import logging
import threading
import time
import uuid
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

    def getGameData(self):
        outerHTML = str(self.driver.find_element(By.CLASS_NAME, 'battle-field').get_property('outerHTML'))
        return outerHTML

    def getLockStatus(self):
        if self.browser_thread_lock.locked():
            return False
        return True

    def startBot(self):
        self.browser_thread_lock.acquire()
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)
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
        action = ActionChains(self.driver).key_down(key, element=None).pause(0.1).key_up(key, element=None)
        action.perform()


def create_from_env():
    bot = GameBot(driver_path=BROWSER_DRIVER_PATH, game_url=GAME_URL)
    return bot


if __name__ == '__main__':
    tempBot = create_from_env()
    tempBot.startBot()
