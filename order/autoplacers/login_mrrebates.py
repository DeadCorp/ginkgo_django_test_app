import json
import logging
import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from order.autoplacers.Browser import Browser


class AutoLoginMrRebates(Browser):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    def __init__(self):
        super().__init__()
        self.email = 'alfredmaccnt@gmail.com'
        self.password = 'AlfredM@gcalas2019)'
        self.url = 'https://mrrebates.com'
        self.send_question_url = 'https://2captcha.com/in.php'
        self.take_answer_url = 'https://2captcha.com/res.php'
        self.api_key = '0aaf0ddc9eb8e3ec3a26189adc24c448'
        self.captcha_not_ready = 'CAPCHA_NOT_READY'

    def run(self):
        logging.info('Open main page')
        self.browser.get(self.url)
        self.login()
        self.check_login()

    def check_login(self):
        top_bar_right = self.browser.find_element(By.CSS_SELECTOR, '.top-bar-right')
        logout_button = top_bar_right.find_element(By.CSS_SELECTOR, '.logout-button')
        if logout_button is not None:
            log_in_email = top_bar_right.text.replace(logout_button.text, '')
            if log_in_email.strip() == self.email.strip():
                logging.info(f'Successful login as {log_in_email}')
            else:
                logging.error('log in email not equal to expected email')
        else:
            logging.error('Not log in')

    def login(self):
        logging.info('Search Log in button')
        self.browser.find_element(By.CSS_SELECTOR, '.top-bar-right > a').click()
        logging.info('Button found. Go to login page')
        logging.info('Search recaptcha on the page')
        recaptcha = self.browser.find_element(By.CSS_SELECTOR, '.g-recaptcha')
        site_key = recaptcha.get_attribute('data-sitekey')
        logging.info(f'Recaptcha found. Site key is [ {site_key} ]')
        self.solve_captcha(site_key)
        logging.info('Start enter credentials')
        self.browser.find_element(By.CSS_SELECTOR, 'input[name="t_email_address"]').send_keys(self.email)
        self.browser.find_element(By.CSS_SELECTOR, 'input[name="t_password"]').send_keys(self.password)
        self.browser.find_element(By.CSS_SELECTOR, '.row * > button[type="submit"]').click()

    def solve_captcha(self, site_key):
        parameters_question = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': self.browser.current_url,
            'json': 1,
        }
        parameters_answer = {
            'key': self.api_key,
            'action': 'get',
            'id': 0,
            'json': 1,
        }
        logging.info('Do question request to get answer id')
        question_response = requests.get(self.send_question_url, params=parameters_question)
        question_response = json.loads(question_response.text)
        logging.info(f'Answer id {question_response["request"]}')
        parameters_answer['id'] = int(question_response['request'])
        time.sleep(15)
        answer = self.captcha_not_ready
        logging.info('Start check answer ready')
        while answer == self.captcha_not_ready:
            time.sleep(5)
            answer_response = requests.get(self.take_answer_url, params=parameters_answer)
            answer = json.loads(answer_response.text)['request']
            logging.info(f'answer {answer}')
        logging.info('Take answer successful')

        recaptcha = self.wait.until(EC.presence_of_element_located((By.ID, 'g-recaptcha-response')))
        self.browser.execute_script(f'arguments[0].value = "{answer}";', recaptcha)


test = AutoLoginMrRebates()
test.run()
