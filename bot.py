import os
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from dotenv import load_dotenv

load_dotenv()

BROWSER_DRIVER_PATH = os.environ.get("BROWSER_DRIVER_PATH")
GAME_URL = os.environ.get("GAME_URL")


def startBot():
    driver = webdriver.Chrome(BROWSER_DRIVER_PATH)
    wait = WebDriverWait(driver, 0.1)
    initial_url = GAME_URL
    driver.get(initial_url)
    current_url = driver.current_url
    while True:
        try:
            wait.until(EC.url_changes(current_url))
            current_url = driver.current_url
        except TimeoutException:
            pass
        page_source = driver.page_source
        with open('page_source.html', 'w', encoding='utf-8') as f:
            if page_source:
                f.write(page_source)
        time.sleep(0.1)


if __name__ == '__main__':
    startBot()
