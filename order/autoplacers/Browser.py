import logging
import os

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


class Browser(object):

    def __init__(self):
        executable_path = os.path.join(os.path.dirname(__file__), 'chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('no-sandbox')
        # options.add_argument('headless')
        options.add_argument('--window-size=1920x1080')
        self.browser = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
        self.wait = WebDriverWait(self.browser, 6)
        self.log_in_try = 2
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger('browser_logger')