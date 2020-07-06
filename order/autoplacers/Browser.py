import os

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


class Browser(object):

    def __init__(self):
        executable_path = os.path.join(os.path.dirname(__file__), 'chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('no-sandbox')
        options.add_argument('headless')
        options.add_argument('--window-size=1920x1080')
        self.browser = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
        self.wait = WebDriverWait(self.browser, 6)

        self.send_question_url = 'https://2captcha.com/in.php'
        self.take_answer_url = 'https://2captcha.com/res.php'
        self.api_key = '0aaf0ddc9eb8e3ec3a26189adc24c448'
        self.captcha_not_ready = 'CAPCHA_NOT_READY'
        self.parameters_question_recaptcha = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': '',
            'pageurl': '',
            'json': 1,
        }
        self.parameters_answer_recaptcha = {
            'key': self.api_key,
            'action': 'get',
            'id': 0,
            'json': 1,
        }
        self.log_in_try = 2
