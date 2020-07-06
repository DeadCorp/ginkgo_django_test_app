import json
import time

import requests


class CaptchaSolver(object):

    def __init__(self, logger, task_id):
        self.send_question_url = 'https://2captcha.com/in.php'
        self.take_answer_url = 'https://2captcha.com/res.php'
        self.api_key = '0aaf0ddc9eb8e3ec3a26189adc24c448'
        self.captcha_not_ready = 'CAPCHA_NOT_READY'
        self.log_info = lambda msg: logger.info(f'{task_id} {msg}')
        self.log_err = lambda msg: logger.error(f'{task_id} {msg}')
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

    def solve(self, site_key, page_url):
        self.log_info('Do request to get answer id')
        self.parameters_question_recaptcha['googlekey'] = site_key
        self.parameters_question_recaptcha['pageurl'] = page_url

        question_response = requests.get(self.send_question_url, params=self.parameters_question_recaptcha)
        question_response = json.loads(question_response.text)

        self.log_info(f'Answer id {question_response["request"]}')
        self.parameters_answer_recaptcha['id'] = int(question_response['request'])
        time.sleep(15)

        answer = self.captcha_not_ready
        self.log_info('Start check answer ready')
        while answer == self.captcha_not_ready:
            time.sleep(5)
            answer_response = requests.get(self.take_answer_url, params=self.parameters_answer_recaptcha)
            answer = json.loads(answer_response.text)['request']
            self.log_info(f'Answer {answer}')

        if 'ERROR' in answer:
            self.log_err('Problem with solve captcha')
            return None
        else:
            self.log_info('Take answer successful')
            return answer

