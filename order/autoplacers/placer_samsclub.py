import logging
import os
import re
import time

from django.conf import settings
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from order.autoplacers.Browser import Browser
from order.models import Order
from supplieraccount.models import SupplierAccount


class AutoPlacerSamsClub(Browser):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    def __init__(self, **kwargs):
        super().__init__()
        self.main_page_url = 'https://www.samsclub.com/'
        self.actions = ActionChains(self.browser)
        order = Order.objects.get(id=kwargs['order_instance_id'])
        account = SupplierAccount.objects.get(id=order.account.id)

        self.username = account.username
        self.email = account.email
        self.password = account.password

        self.product_url = order.product.product_url
        self.options = order.product.variants_tag
        self.is_variant = order.product.is_variant
        self.count = kwargs['count']
        self.product_price = order.product.price
        self.product_id = order.product.product_id
        self.option_id = order.product.option_id

        self.product_status = '0'
        self.cart_status = '0'
        self.task_id = kwargs['celery_task_id']
        self.log_info = lambda msg: logging.info(f'Order {self.task_id} {msg}')
        self.log_err = lambda msg: logging.error(f'Order {self.task_id} {msg}')

        self.screenshot = f'Order_{self.task_id}_product_{order.product.sku}_'
        self.screenshot_dict = {}

        self.product_cart_price = ''
        self.product_cart_quantity = ''

        self.zip_code = '60169'

    def clear_cart(self):
        self.log_info('Open cart page')
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.container-cart'))).click()
        try:
            items = self.wait.until(EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, '.sc-cart-item * .sc-cart-display-info-item-no')))
        except TimeoutException:
            self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.sc-cart-empty')))
            self.cart_status = 'EMPTY'
            self.take_screenshot('clear_cart')
            return self.log_info('Cart is already clear')
        for item in items:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-cart-item-actions-remove'))).click()
            time.sleep(3)
        try:
            self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.sc-cart-empty')))
            self.cart_status = 'EMPTY'
            self.take_screenshot('clear_cart')
            return self.log_info('Cart is clear')
        except TimeoutException:
            self.log_err('Cart is not clear. Try again')
            self.cart_status = 'NO_EMPTY'
            self.take_screenshot('cart_not_clean')
            return self.clear_cart()

    def check_product_in_cart(self):
        items = self.wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, '.sc-cart-item * .sc-cart-display-info-item-no')))
        if len(items) == 1:
            self.log_info('In the cart 1 product')
            item_number = re.findall(r'\d+', items[0].text)[0]
            if item_number == self.option_id:
                self.log_info(f'Product option in the cart is correct {item_number}')
                self.product_cart_quantity = self.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '.sc-quantity-editor * input'))).get_attribute('value')

                if int(self.product_cart_quantity) == 1:
                    self.product_cart_price = self.wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '.sc-cart-item-details-subtotal'))).text.replace('$', '').replace(',', '')
                else:
                    self.product_cart_price = self.wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '.sc-cart-item-details-list-price'))).text
                    self.product_cart_price = re.findall(r'[0-9,]+.\d+', self.product_cart_price)
                    self.product_cart_price = self.product_cart_price[0].replace(',', '')
                if round(float(self.product_cart_price), 2) == float(self.product_price):
                    self.log_info(f'Product price in the cart correct - {float(self.product_cart_price)}')
                    if int(self.product_cart_quantity) == int(self.count):
                        self.log_info(f'Product quantity is correct - {self.product_cart_quantity}')
                        self.product_status = 'SUCCESS'
                        self.check_zip_code_in_cart()
                        self.take_screenshot('cart_is_correct')
                        return None
                    else:
                        self.log_err(f'Product quantity is incorrect - {self.product_cart_quantity}')
                else:
                    self.log_err(f'Product price in the cart incorrect - {float(self.product_cart_price)}')
            else:
                self.log_err(f'Product option in the cart  incorrect {item_number}')
                self.product_status = 'WRONG_ITEM'
        else:
            self.log_err(f'More 1 products in the cart')
            self.cart_status = 'NO_EMPTY'
        self.product_status = 'WRONG_DATA'
        self.take_screenshot('cart_is_incorrect')
        return None

    def check_zip_code_in_cart(self):
        self.log_info('Check zip code in cart')
        try:
            zip_code = self.wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.sc-zip-code-input-text'))).text
        except TimeoutException:
            zip_code = '0'
        if int(zip_code) == int(self.zip_code):
            self.log_info('Zip code in the cart correct')
        else:
            self.log_err('Zip code in the cart incorrect')
            # try:
            #     self.log_info('Try enter zip code')
            #     self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-zip-code-input-change'))).click()
            # except TimeoutException:
            #     try:
            #         self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-zip-code-input-button'))).click()
            #     except TimeoutException:
            #         pass
            # try:
            #     zip_input = self.wait.until(EC.visibility_of_element_located(
            #         (By.CSS_SELECTOR, '.sc-zip-code-input-input * input')))
            #     self.browser.execute_script(f'arguments[0].value = {self.zip_code};', zip_input)
            #     self.wait.until(EC.element_to_be_clickable(
            #         (By.CSS_SELECTOR, '.sc-zip-code-input-form > button'))).click()
            # except TimeoutException:
            #     pass
            # try:
            #     self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-zip-code-input-form > button')))
            #     self.log_err('Problem with entered zip code. Try again')
            #     self.check_zip_code_in_cart()
            # except TimeoutException:
            #     pass
            # self.log_info('Zip code entered successful')

    def check_member_only_price(self):
        # Now need for skip adding , but we can't login
        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.sc-action-buttons-sams-exclusive')))
            self.log_err('It`s only membership product. Can`t continue without login')
            self.product_status = 'ADDING_PROBLEM'
            return None
        except TimeoutException:
            return self.product_status

    def place(self):
        self.log_info('Open product page')
        self.browser.get(self.product_url)
        if self.check_member_only_price() is None:
            self.take_screenshot('product_not_ready_to_adding')
            return self.log_err('Cannot continue place product to cart')
        verify = self.verify_product()
        if verify is None or verify == 'OOS':
            self.take_screenshot('product_not_ready_to_adding')
            return self.log_err('Cannot continue place product to cart')
        if self.check_oos() is None:
            self.take_screenshot('product_not_ready_to_adding')
            return self.log_err('Cannot continue place product to cart')
        self.check_zip_code()
        if self.is_variant:
            if self.select_options() is None:
                self.take_screenshot('product_not_ready_to_adding')
                return self.log_err('Cannot continue place product to cart')
        if self.enter_quantity() is None:
            self.take_screenshot('product_not_ready_to_adding')
            return self.log_err('Cannot continue place product to cart')
        self.click_add_to_cart()
        if self.product_status == 'ADDING_PROBLEM':
            return self.log_err('Problem with add to cart button')
        self.check_product_in_cart()

    def click_add_to_cart(self):
        try:
            to_up = self.browser.find_element(By.CSS_SELECTOR, '.sc-product-header-item-number')
            self.actions.move_to_element(to_up).perform()
            self.take_screenshot('product_ready_to_adding')
            self.log_info('Try click on add to cart button')
            self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.online.sc-cart-qty-button * button'))).click()
            self.log_info('Try go to cart from modal window')
            try:
                self.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '.sc-a2c-addon-wrap * .sc-btn-primary'))).click()
            except (TimeoutException, ElementClickInterceptedException):
                self.log_info('Promotion modal except to actions. Try close it')
                try:
                    self.wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '.sc-protection-plan * .sc-btn-secondary'))).click()
                except TimeoutException:
                    pass
                self.log_info('Try again go to cart')
                self.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '.sc-a2c-addon-wrap * .sc-btn-primary')))
                self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.sc-a2c-addon-wrap * .sc-btn-primary'))).click()

        except TimeoutException:
            self.log_err('Cannot click on add to cart button')
            self.product_status = 'ADDING_PROBLEM'
            return None

    def check_zip_code(self):
        try:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-shipping-info-enter-zip-link'))).click()
            self.log_info('Click on enter zip code')
            self.enter_zip_code()
        except TimeoutException:
            self.log_info('Not found button enter zip code. Try change zip code')
            try:
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-shipping-info-options-link'))).click()
                self.log_info('Click on change zip code')
                zip_code = self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.sc-shipping-options-zipcode'))).text
                if zip_code == self.zip_code:
                    return self.log_info('Excepted zip code is already selected')
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-shipping-options-change'))).click()
                self.enter_zip_code()
            except TimeoutException:
                self.log_err('Cannot change zip code')
                return 'error'

    def enter_zip_code(self):
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.sc-shipping-options * > input'))).clear()
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.sc-shipping-options * > input'))).send_keys(self.zip_code)
        self.log_info('Enter zip code')
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-shipping-options * > button'))).click()

        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sc-shipping-options-error')))
            self.log_err('It incorrect zip code')
        except TimeoutException:
            self.log_info('Zip code is correct')

    def verify_product(self):
        try:
            header = self.wait.until(
                EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '.sc-product-header-item-number')))
        except TimeoutException:
            try:
                header = self.wait.until(EC.visibility_of_any_elements_located(
                    (By.CSS_SELECTOR, '.sc-oos-card-header-row-item')))
                self.product_status = 'OOS'
            except TimeoutException:
                self.log_err('Cannot verify product on the page. Cannot find item number')
                self.product_status = 'ADDING_PROBLEM'
                return None

        for item in header:
            if 'item' in item.text.lower():
                item_number = re.findall(r'\d+', item.text)
                if item_number:
                    if int(item_number[0]) == int(self.option_id):
                        self.log_info('Product on the page is correct')
                        return self.product_status
                    else:
                        self.log_err('Product on the page is incorrect')
                        self.product_status = 'ADDING_PROBLEM'
                        return None

    def enter_quantity(self):
        self.log_info(f'Start enter quantity. Need set quantity to {self.count}')
        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.online.sc-cart-qty-button * input'))).send_keys(Keys.DELETE)
            self.wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.online.sc-cart-qty-button * input'))).send_keys(self.count)
            try:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sc-input-box-error-block')))
                self.product_status = 'ADDING_PROBLEM'
                return None
            except TimeoutException:
                return self.product_status
        except (TimeoutException, ElementNotInteractableException):
            self.log_err('Cannot enter quantity')
            self.product_status = 'WRONG_COUNT'
            return None

    def check_oos(self):
        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.sc-channel-online * .sc-channel-stock-out-of-stock')))
            self.log_err('It`s out of stoke product')
            self.product_status = 'OOS'
            return None
        except TimeoutException:
            return self.product_status

    def select_options(self):
        to_up = self.browser.find_element(By.CSS_SELECTOR, '.sc-product-header-item-number')
        self.log_info('Start select options')
        try:
            options = self.wait.until(EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, '.prod-ProductVariantSwatch *')))
        except TimeoutException:
            try:
                options = self.wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '.sc-select-options > .sc-select-option')))
            except TimeoutException:
                self.log_err('Cannot found options')
                self.product_status = 'ADDING_PROBLEM'
                return None
        for option in options:
            data_variant_id = option.get_attribute('data-variant-id')
            if (data_variant_id is not None) and data_variant_id.lower() in self.options:
                self.log_info(f'Try click on option - {data_variant_id}')
                self.actions.move_to_element(to_up).perform()
                option.click()
            elif data_variant_id is None:
                aria_label = option.get_attribute('aria-label')
                if aria_label is not None:
                    aria_label = aria_label.lower()
                    for check_option in self.options:
                        if aria_label.strip() in check_option.strip():
                            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-select-box'))).click()
                            self.log_info(f'Try click on option - {aria_label}')
                            self.actions.move_to_element(to_up).perform()
                            option.click()
                            break
        return self.product_status

    def parse_options(self):
        self.options = [f'{item.split(":")[0].strip()}:{item.split(":")[1].strip()}'.lower()
                        for item in self.options.split(';')]

    def take_screenshot(self, msg=''):
        dir_name = os.path.join(settings.MEDIA_ROOT, 'status_image')
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        screenshot_name = self.screenshot + msg + '.png'
        self.browser.save_screenshot(os.path.join(dir_name, screenshot_name))
        self.screenshot_dict[msg] = screenshot_name
        self.log_info(f'Save screenshot {msg} \n{dir_name}/{screenshot_name}\n{self.browser.current_url}')

    def run(self):
        if self.is_variant:
            self.parse_options()
        self.log_info('Open main page')
        self.browser.get(self.main_page_url)
        # Login here
        self.clear_cart()
        self.place()
        result = {
            'quantity': self.product_cart_quantity,
            'price': self.product_cart_price,
            'order_status': self.product_status,
            'screenshots': self.screenshot_dict,
        }
        if self.cart_status != 'EMPTY':
            result['order_status'] = 'WRONG_ITEM'
        self.log_info(f'Order status {self.product_status}. Close browser')
        self.browser.close()
        self.browser.quit()
        return result
