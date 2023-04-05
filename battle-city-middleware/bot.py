import json
import logging
import re
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
    # 基础数据
    game_url = ""
    driver_path = ""
    driver = None

    # 游戏数据
    bot_id = ""
    reward = 0
    score = 0  # 游戏默认值
    level = 1  # 游戏默认值
    HP = 2  # 游戏默认值
    done = False

    # 锁
    browser_thread_lock = threading.Lock()

    def __init__(self, game_url, driver_path):
        self.game_url = game_url
        self.driver_path = driver_path
        self.bot_id = str(uuid.uuid4())

    def getID(self):
        return str(self.bot_id)

    def getGameDataFromXPath(self) -> dict:
        xpath = r'/html/body/div/div/div/div[2]/pre[2]'
        content = self.driver.find_element(By.XPATH, xpath).text
        return json.loads(content)

    def getGameData(self):
        outerHTML = str(self.driver.find_element(By.CLASS_NAME, 'battle-field').get_property('outerHTML'))
        return outerHTML

    def getLockStatus(self):
        if self.browser_thread_lock.locked():
            return False
        return True

    def updateReward(self, fail=False):
        # 过关：+5000，扣血：-1000，分数：直接叠加游戏分数
        if fail:
            self.done = True
        data = self.getGameDataFromXPath()
        new_hp = int(data.get('lives', self.HP))
        new_score = int(data.get('score', self.score))
        level_pattern = re.compile('(\d+)$')
        level_match = level_pattern.search(self.driver.current_url).group()
        new_level = int(level_match)
        if new_level and new_level != self.level:
            self.reward = self.reward + 5000 * (new_level - self.level)
            self.level = new_level
        if new_score != self.score:
            self.reward = self.reward + (new_score - self.score)
            self.score = new_score
        if new_hp != self.HP:
            self.reward = self.reward + (new_hp - self.HP) * 1000
            self.HP = new_hp

    def getStatus(self) -> dict:
        self.updateReward()
        return {
            'reward': self.reward,
            'done': self.done
        }

    def startBot(self):
        with self.browser_thread_lock:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument("--disable-gpu")
            # chrome_options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)
            self.driver.get(self.game_url)
            current_url = self.driver.current_url
            wait = WebDriverWait(self.driver, 0.1)
            while True:
                try:
                    wait.until(expected_conditions.url_changes(current_url))
                    self.updateReward()
                    current_url = self.driver.current_url
                    time.sleep(0.1)
                except TimeoutException:
                    logging.info('selenium.current_url未改变，当前请求链接为：{}'.format(current_url))
                    if current_url.endswith('gameover'):
                        self.updateReward(fail=True)
                        logging.info('游戏结束，60s后游戏对象自我销毁')
                        # self.driver.get(self.game_url)
                        time.sleep(60)
                        break
                except NoSuchElementException:
                    logging.warning('已脱离游戏状态，无法捕获对应元素')
                except Exception as e:
                    logging.error(str(e))
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
