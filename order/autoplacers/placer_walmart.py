import json
import logging
import os
import re
import time

import requests
from django.conf import settings
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, \
    StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from order.autoplacers.Browser import Browser
from order.autoplacers.captcha_solver import CaptchaSolver
from order.models import Order
from supplieraccount.models import SupplierAccount


class AutoPlacerWalmart(Browser):


    def __init__(self, **kwargs):
        super().__init__()
        self.product_cart_quantity = '0'
        self.product_cart_price = '0'
        order = Order.objects.get(id=kwargs['order_instance_id'])
        account = SupplierAccount.objects.get(id=order.account.id)

        self.main_page_url = order.product.product_url[:(order.product.product_url.index('/ip/'))]
        self.supplier_password = account.password
        self.supplier_email = account.email
        self.id_product = order.product.product_id
        self.product_url = order.product.product_url
        self.count = kwargs['count']
        self.price = order.product.price.replace('$', '')
        self.qty = 0
        self.task_id = kwargs['celery_task_id']

        self.log_info = lambda msg: self.logger.info(f'{self.task_id} {msg}')
        self.log_err = lambda msg: self.logger.error(f'{self.task_id} {msg}')

        self.product_status = '0'
        self.cart_status = '0'

        self.screenshot = f'Order_{self.task_id}_product_{order.product.sku}_'
        self.screenshot_dict = {}
        self.login_status = False

    def get_cart(self):
        try:
            to_cart1 = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/cart']")))
            self.log_info('Open cart page')
            to_cart1.click()
        except TimeoutException:
            self.log_info('do not find button - to cart, go to cart by link')
            return self.browser.get('https://www.walmart.com/cart')

    def check_current_product(self):
        cart_qty = self.browser.find_element(By.CSS_SELECTOR, "span.copy-mini").text
        cart_qty = self.take_num(cart_qty)  # get list with only 1 number
        self.product_cart_quantity = str(cart_qty[0])
        try:
            cart_price = self.browser.find_element(By.CSS_SELECTOR,
                                                   "span.each-price >* span[class='visuallyhidden']").text.replace(
                '$', '')

        except NoSuchElementException:
            cart_price = self.browser.find_element(By.CSS_SELECTOR,
                                                   "div.price-main >* span[class='visuallyhidden']").text.replace(
                '$', '')
        cart_price = round(float(cart_price), 2)
        self.product_cart_price = str(cart_price)
        if int(self.count) == int(cart_qty[0]):
            self.log_info(f'Product quantity in the cart correct: {cart_qty}')
            if float(cart_price) == float(self.price):
                self.log_info(f'Single product price in the cart correct: {cart_price}')
                self.log_info('All correct in the cart')
                self.product_status = 'SUCCESS'

            else:
                self.log_err(f'Single product price in the cart invalid: {cart_price} excepted: {self.price}')
                self.product_status = 'WRONG_DATA'

        else:
            self.log_err(f'Product quantity in the cart invalid: {cart_qty} excepted: {self.count}')
            self.product_status = 'WRONG_DATA'

    def check_cart(self):
        self.get_cart()
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cart-item-row")))
            cart = self.browser.find_elements_by_class_name('cart-item-row')
            cart_quantity_msg = f'Products in the cart: {len(cart)}'

            for item in cart:
                cart_item = item.find_element_by_class_name('js-btn-product')
                item_id = cart_item.get_attribute('data-us-item-id')
                if len(cart) == 1:
                    self.log_info(cart_quantity_msg + ' - OK')

                    if item_id != self.id_product:
                        self.log_err(
                            f'Product id in the cart: {item_id} not equal to order product id: {self.id_product}')
                        self.take_screenshot('cart_is_incorrect')
                        self.cart_status = 'WRONG_ITEM'
                    else:
                        self.log_info(f'Product id {item_id} in the cart correct')

                        self.check_current_product()

                        if self.product_status == 'SUCCESS':
                            self.take_screenshot('cart_is_correct')
                        else:
                            self.take_screenshot('cart_is_incorrect')
                        self.cart_status = 'SUCCESS'
                else:
                    self.log_err(cart_quantity_msg)
                    self.take_screenshot('cart_is_incorrect')
                    self.product_status = 'WRONG_ITEM'
                    self.cart_status = 'WRONG_ITEM'
                    return self.cart_status
        except TimeoutException:
            self.log_info('No products in the cart!')
            self.take_screenshot('cart_is_incorrect')
            self.cart_status = 'EMPTY'

    def clear_cart(self):
        self.get_cart()
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cart-item-row")))
            cart = self.browser.find_elements_by_class_name('cart-item-row')
            self.take_screenshot('cart_before_cleaning')
            self.browser.implicitly_wait(10)
            for i, item in enumerate(cart):
                self.log_info(f'Deleting products. {len(cart) - i} of {len(cart)} products remaining')
                try:
                    remove_item = item.find_element(By.CSS_SELECTOR, "button[data-automation-id='cart-item-remove']")
                    remove_item.click()

                except ElementClickInterceptedException:
                    try:
                        remove_item = item.find_element(By.CSS_SELECTOR,
                                                        "button[data-automation-id='cart-item-remove']")
                        remove_item.click()
                    except ElementClickInterceptedException:
                        pass
            else:
                self.cart_status = 'EMPTY'

        except TimeoutException:
            self.log_info('Cant get presence products. Set cart status as: EMPTY')
            self.cart_status = 'EMPTY'
        time.sleep(3)
        self.take_screenshot('clear_cart')

    def get_main_page(self):
        self.log_info('Get main page')
        return self.browser.get(self.main_page_url)

    def __verify_product(self):
        time.sleep(0.5)
        try:
            verify_product = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[itemprop="sku"]')))
            product_id = verify_product.get_attribute('content')
            if str(product_id) != str(self.id_product):
                self.log_err(f'Incorrect product on the page: [{product_id}]')
                self.product_status = 'ADDING_PROBLEM'
                return self.product_status
            else:
                self.log_info(f'Product on the page is correct: [{product_id}]')
        except (TimeoutException, NoSuchElementException):
            self.log_info('Not found id on the page. Will check id in the cart')

    def add_to_cart(self):

        self.log_info('Start add product to cart')
        self.log_info('Open product page')
        self.browser.get(self.product_url)

        status = self.__verify_product()
        if status is not None:
            return self.product_status

        self.log_info('Start select quantity')
        self.select_qty()

        if self.qty != self.count:
            self.product_status = 'WRONG_COUNT'
            return self.product_status

        try:
            self.log_info('Wait when product loading')
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span[itemprop='price']")))
        except TimeoutException:
            self.log_err('Product not loaded after select quantity')
            self.product_status = 'ADDING_PROBLEM'
            return self.product_status

        try:
            self.log_info('Search button: Add to cart')
            button_el = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'spin-button-children')))

            if button_el.text.lower() == 'get in-stock alert':
                self.log_err('Product OOS, because button have "Get In-Stock Alert" message')
                self.product_status = 'OOS'
                self.take_screenshot('out_of_stoke')
                return self.product_status, self.cart_status
            else:
                self.take_screenshot('product_ready_to_adding')
                button_el.click()

                try:
                    modal_window = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-content')))
                    if modal_window.text:
                        self.log_err(
                            f'Product not added to cart, found modal window with text:\n{modal_window.text.replace("Close", " ")}')
                        self.take_screenshot('modal_window')
                        button = modal_window.find_elements_by_tag_name('button')
                        button[-1].click()
                        self.product_status = 'WRONG_COUNT'
                        return self.product_status

                except TimeoutException:
                    self.log_info('Start check product in the cart')
                    self.check_cart()

                    # self.log_err('Adding button does not exist')
                    # self.product_status = 'ADDING_PROBLEM'
                    # return self.product_status, self.cart_status

        except TimeoutException:
            self.log_err('Add to cart button not found, 50% product OOS')
            self.product_status = 'OOS'
            self.take_screenshot('product_not_ready_to_adding')
            return self.product_status, self.cart_status

        return self.product_status, self.cart_status

    def select_qty(self):
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span[itemprop='price']")))
        except TimeoutException:
            pass

        self.log_info(f'Need set product quantity to: {self.count}')
        all_options = self.browser.find_elements(By.CSS_SELECTOR, "select[aria-label='Quantity'] > option")
        for option in all_options:

            if int(option.get_attribute("value")) == int(self.count):
                option.click()
                self.qty = option.get_attribute("value")
                self.log_info(f'Product quantity changed to {self.qty}')
                break
            elif int(self.count) > int(all_options[-1].get_attribute("value")):
                all_options[-1].click()
                self.qty = all_options[-1].get_attribute("value")
                self.log_err(f'Excepted quantity not available, max available quantity: {self.qty}')
                self.take_screenshot('invalid_selecting_qty')
                break
        else:
            self.log_err('Can not find quantity select options')
            self.take_screenshot('quantity_options_invalid')

    def take_screenshot(self, msg=''):
        dir_name = os.path.join(settings.MEDIA_ROOT, 'status_image')
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        screenshot_name = self.screenshot + msg + '.png'
        self.browser.save_screenshot(os.path.join(dir_name, screenshot_name))
        self.screenshot_dict[msg] = screenshot_name
        self.log_info(f'Save screenshot {msg} \n{dir_name}/{screenshot_name}\n{self.browser.current_url}')

    @staticmethod
    def take_num(line):
        response = re.findall(r'\d*\.\d+|\d+', line)
        return response

    def run(self):
        # if method bad_credentials in method login return True, method login return bool value else None
        # or if no need solve captcha and url after click not change, method login return bool value else None
        if self.login() is None and self.login_status is True:

            self.get_main_page()
            self.log_info('Clear cart after login')
            self.clear_cart()
            if self.cart_status == 'EMPTY':

                try:
                    self.add_to_cart()

                except (TimeoutException, StaleElementReferenceException, ElementNotInteractableException):
                    self.log_err('Some exception when add to cart. Return status ADDING_PROBLEM')
                    self.product_status = 'ADDING_PROBLEM'

                if self.product_status == 'SUCCESS' and self.cart_status == 'SUCCESS':
                    self.log_info(f'Order status: {self.product_status}. Close browser')

                elif self.product_status == 'SUCCESS' and self.cart_status != 'SUCCESS' and self.cart_status != '':
                    self.product_status = 'WRONG_ITEM'
                    self.log_err(f'Order status: {self.product_status}. Close browser')

                else:
                    self.log_err(f'Order status: {self.product_status}. Close browser')

            else:
                self.log_err('Cart not empty after cleaning')
        else:
            self.product_status = 'ADDING_PROBLEM'
        self.browser.quit()
        return {
            'quantity': self.product_cart_quantity,
            'price': self.product_cart_price,
            'screenshots': self.screenshot_dict,
            'order_status': self.product_status,
        }

    def to_login(self):
        self.get_main_page()
        try:
            self.log_info('Start login process')
            time.sleep(1)
            to_account = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Your Account']")))
            to_account.click()
            try:
                time.sleep(0.5)
                self.log_info('Try open login page')

                to_login = self.browser.find_element(By.CSS_SELECTOR, "a[title='Sign In']")
                self.browser.execute_script("arguments[0].click();", to_login)
                self.log_info('Open login page')
            except TimeoutException:

                loginned_user = self.browser.find_element(By.CSS_SELECTOR,
                                                          'span[data-tl-id="header-account-menu-title"]')
                self.log_err('Login process failed')
                self.log_err(f'Already login user {loginned_user.get_attribute("text")}')
                self.log_info('Do log out')
                self.log_out()
        except TimeoutException:
            self.log_err("Didn't find account section ")
            self.retry_login()

    def log_out(self):
        try:

            log_out = self.browser.find_element(By.CSS_SELECTOR, "a[title='Sign Out']")
            self.browser.execute_script("arguments[0].click();", log_out)
            self.log_info('Log out successful')
        except TimeoutException:
            self.log_err('Log out failed')
            self.log_info('Retry login process')
            self.to_login()

    def bad_credentials(self):
        self.log_info('Check credentials correcting')
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#global-error')))
            self.log_err('Incorrect credentials')
            self.take_screenshot('incorrect_credentials')
            return True
        except TimeoutException:
            return False

    def login(self):
        self.to_login()
        login = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "form#sign-in-form > button[type='submit']")))

        self.log_info('Start enter credentials')
        self.browser.find_element(By.ID, "email").send_keys(self.supplier_email)
        self.browser.find_element(By.ID, "password").send_keys(self.supplier_password)
        self.log_info('Credentials entered, click SignIn button')
        current_url = self.browser.current_url
        login.click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.g-recaptcha')))
            self.log_info('Need solve captcha')
            self.solve_captcha()
        except TimeoutException:
            try:
                self.wait.until(EC.url_changes(current_url))
                self.log_info('No need solve captcha')
            except TimeoutException:
                self.log_err('Problem with logIn')
                self.take_screenshot('problem_with_login')
                return False
        if self.bad_credentials():
            return False
        if not self.check_is_log_in():
            self.log_err("User wasn't logged in")
            self.take_screenshot(f'user_was_not_login_try_{self.log_in_try}')
            self.retry_login()

    def check_is_log_in(self):
        self.log_info('Check login status')
        self.get_main_page()
        try:

            to_account = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Your Account']")))
            self.log_info('Open account section')
            to_account.click()
            time.sleep(1)
            try:
                self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#vh-account-menu-root * [title='Sign Out']")))
                self.log_info('Button logOut found. Login successful')
                self.take_screenshot('successful_login')
                self.login_status = True
                return self.login_status
            except (TimeoutException, NoSuchElementException):
                self.log_err('Not found button logOut. Login failed')
                return self.login_status
        except TimeoutException:
            self.log_err('Can not find account section')
            return self.login_status

    def solve_captcha(self):
        captcha = self.browser.find_element(By.CSS_SELECTOR, '.g-recaptcha')
        data_callback = captcha.get_attribute('data-callback').strip()
        site_key = captcha.get_attribute('data-sitekey')
        captcha_solver = CaptchaSolver(self.logger, self.task_id)
        answer = captcha_solver.solve(site_key, self.browser.current_url)

        if answer:
            recaptcha = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#g-recaptcha-response')))
            self.browser.execute_script(f"arguments[0].value='{answer}';", recaptcha)
            self.browser.execute_script(f"{data_callback}('{answer}');")
            time.sleep(10)

    def retry_login(self):
        if self.log_in_try > 0:
            self.log_in_try -= 1
            self.log_info(f'Try logIn again {self.log_in_try} times left')
            self.login()
        else:
            self.log_err('Log In try ended')
