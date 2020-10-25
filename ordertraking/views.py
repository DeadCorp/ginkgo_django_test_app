import time

from django.shortcuts import render, redirect
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from order.autoplacers.Browser import Browser


def track_order(request):
    s = OrderTracking()
    s.run()
    return redirect('product:products')


class OrderTracking(Browser):

    def __init__(self):
        super().__init__()
        self.track_url = 'https://www.walmart.com/account/trackorder'
        self.email = 'wmaccnt44@gmail.com'
        self.order_track_id = '3772040-246487'


        pass

    def run(self):

        self.browser.get(self.track_url)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#email'))).send_keys(self.email)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#fullOrderId'))).send_keys(self.order_track_id)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.spin-button-children'))).click()
        time.sleep(10)
        self.browser.quit()
        pass
