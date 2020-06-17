import logging
import os
import time

from django.conf import settings
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from order.autoplacers.Browser import Browser
from order.models import Order
from supplieraccount.models import SupplierAccount


class AutoPlacerKmart(Browser):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    def __init__(self, **kwargs):
        super().__init__()
        self.main_page_url = 'https://www.kmart.com/'
        order = Order.objects.get(id=kwargs['order_instance_id'])
        account = SupplierAccount.objects.get(id=order.account.id)

        self.product_url = order.product.url
        self.options = order.product.variants_tag
        self.parse_options()
        self.count = kwargs['count']
        self.product_price = order.product.price.replace('$', '')
        self.option_id = order.product.option_id
        self.product_id = order.product.product_id

        self.product_status = ''
        self.cart_status = ''
        self.task_id = kwargs['celery_task_id']
        self.log_info = lambda msg: logging.info(f'Order {self.task_id} {msg}')
        self.log_err = lambda msg: logging.error(f'Order {self.task_id} {msg}')

        self.screenshot = f'Order_{self.task_id}_product_{order.product.sku}_'
        self.screenshot_dict = {}

        self.animate_style = None
        self.product_cart_price = ''
        self.product_cart_quantity = ''

    def parse_options(self):
        if self.options and self.options != 'is unknown':
            self.options = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in self.options.split('/')}

    def open_cart_page(self):
        self.log_info('Open cart page')
        try:
            to_cart_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#cartArea > a')))
            to_cart_button.click()
        except TimeoutException:
            self.log_err('To cart button not found')

    def clear_cart(self):
        try:
            cart_items = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.product-in-cart')))
            if len(cart_items) > 0:
                self.log_info('Cart not clear, start cleaning')

                for item in cart_items:
                    try:
                        remove_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '* a.remove-item')))
                        remove_button.click()
                        confirm_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[link-name="Remove Item"]')))
                        confirm_button.click()
                        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#logo > a')))
                        # after remove product, page loading, and after that loading again
                        # need sleep for wait second loading
                        time.sleep(3)
                    except TimeoutException:
                        pass
            else:
                self.log_info('Cart already clear')
            try:
                cart_items = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                                                    'div.product-in-cart')))
            except TimeoutException:
                cart_items = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                                                    'div.product-in-cart')))
            if len(cart_items) == 0:
                self.log_info('Cart cleaned successful')
                self.cart_status = 'EMPTY'
                self.take_screenshot('clear_cart')
            else:
                self.log_err('Cart was not cleaned.')
                self.cart_status = 'NO_EMPTY'
                self.take_screenshot('cart_not_clean')

        except TimeoutException:
            self.log_info('Can not find products in the cart, maybe cart already clear')
            self.cart_status = 'EMPTY'
            self.take_screenshot('clear_cart')

    def add_product_to_cart(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.variants-form')))

            self.log_info('Start select options')
            self.select_options()
            if self.product_status == 'OOS':
                return None
        except (TimeoutException, NoSuchElementException):
            self.log_info('Product not have options')

        self.select_quantity()

        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.feedback-message')))
            self.log_err('Select quantity not availability')
            self.take_screenshot('product_not_ready_to_adding')
            return None
        except TimeoutException:
            self.log_info('No OOS message ')

        self.log_info('Start select shipping')
        shipping = self.select_shipping()
        if shipping is None:
            self.take_screenshot('product_not_ready_to_adding')
            return None
        else:
            self.log_info('Successful select shipping')
            self.take_screenshot('product_ready_to_adding')
        try:
            self.add_to_cart_buttons_click()
        except TimeoutException:
            self.log_err('Can`not found on button add to cart')
        except NoSuchElementException:
            self.log_err('Can`not click on button add to cart')

        self.log_info('Start check product in the cart')
        self.check_product_in_cart()

    def add_to_cart_buttons_click(self):
        add_to_cart_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'form#addToCart > button')))
        time.sleep(3)
        add_to_cart_button.click()
        go_to_cart_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.go-to-cart')))
        time.sleep(3)
        go_to_cart_button.click()

    def select_shipping(self):
        self.log_info('Try click on shipping')
        try:
            shipping_section = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                 '.productFulfillmentShipPanel-page')))
        except TimeoutException:
            shipping_section = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                 '.productFulfillmentShipPanel-page')))

        try:
            shipping = shipping_section.find_element(By.CSS_SELECTOR, 'div[data-method="shipping"]')
            shipping.click()
            return ''
        except NoSuchElementException:
            shipping_message = shipping_section.find_element(By.CSS_SELECTOR, 'span > span').text
            self.log_info(shipping_message)
            if 'quantity' in shipping_message:
                self.product_status = 'WRONG_COUNT'
            else:
                self.product_status = 'OOS'
            return None

    def select_quantity(self):
        self.log_info('Start select quantity')
        self.log_info(f'Need set quantity to {self.count}')

        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#rightrail')))
            quantity = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="quantity"]')))
        except TimeoutException:
            quantity = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="quantity"]')))
        quantity_value = quantity.get_attribute('value')
        difference = int(self.count) - int(quantity_value)

        if difference == 0:
            self.log_info(f'Quantity already selected to {quantity_value}')
            return None
        else:
            clicks = 0
            while clicks != difference:
                try:
                    shipping_section = self.wait.until(EC.visibility_of_element_located( (By.CSS_SELECTOR, '.productFulfillmentShipPanel-page > div')))
                    self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.button-quantity-inc'))).click()
                    clicks += 1
                except TimeoutException:
                    try:
                        shipping_section = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.productFulfillmentShipPanel-page > span > span')))
                        self.log_info('This quantity unavailability')
                        self.product_status = 'WRONG_COUNT'
                        return None
                    except TimeoutException:
                        self.log_err('Another err')
                        return None

            quantity = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="quantity"]')))
            quantity_value = quantity.get_attribute('value')
            self.log_info(f'Quantity set to {quantity_value}')
            if quantity_value != self.count:
                self.select_quantity()

    def select_options(self):

        self.recognize_options_method()
        for option_name in self.options:
            option_values = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'div[data-name="{option_name}"]')))
            if self.animate_style:
                option_values = option_values.find_elements(By.CSS_SELECTOR, 'div > div > ul > li')
            else:
                option_values = option_values.find_elements(By.CSS_SELECTOR, 'ul > li')
            for option in option_values:
                if not option.text:
                    option_img = option.find_element(By.CSS_SELECTOR, 'img')
                    option_text = option_img.get_attribute('title')
                else:
                    option_text = option.text
                if option_text == self.options[option_name]:
                    self.log_info(f'Try click on option {option_name} : {option_text}')
                    option.click()
                    if self.animate_style:
                        select_check = self.browser.find_element(By.CSS_SELECTOR, f'div[data-name="{option_name}"] > label > .field-value').text
                    else:
                        select_check = self.browser.find_element(By.CSS_SELECTOR, f'div[data-name="{option_name}"] > header > span').text

                    if option_text.strip() == select_check.strip():
                        self.log_info(f'Selected {select_check} - OK')
                    else:
                        self.log_err(f'Selected {select_check} - ERROR')
                        self.product_status = 'OOS'
                    break

    def recognize_options_method(self):
        try:
            animate = self.browser.find_element(By.CSS_SELECTOR, '.variants-form > .a-imateStyle')
            try:
                hidden_attr = self.browser.find_elements(By.CSS_SELECTOR, '.addTablestyle > div')
                if len(hidden_attr) == 0:
                    self.log_info('Need click on select button to display all options')
                    select_button = self.browser.find_element(By.CSS_SELECTOR, '.productVariant-module > .selectCotainer > a')
                    select_button.click()
                    self.animate_style = True
                else:
                    self.log_info('No need click on select button to display all options')
                    self.animate_style = True
            except NoSuchElementException:
                self.log_err('Not found animateStyle section')
                self.animate_style = False
        except NoSuchElementException:
            self.animate_style = False

    def check_product_in_cart(self):
        cart_items = []
        try:
            cart_items = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.product-in-cart')))
        except TimeoutException:
            try:
                cart_items = self.wait.until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.product-in-cart')))
            except TimeoutException:
                pass
        if len(cart_items) == 0:
            self.log_err('No products in cart')
            self.product_status = 'ADDING_PROBLEM'
            self.take_screenshot('cart_is_incorrect')
            return None
        elif len(cart_items) == 1:
            self.log_info('In cart 1 product')
            try:
                cart_quantity = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                  'span.qty-input > span')))
                cart_quantity = cart_quantity.text
            except TimeoutException:
                try:
                    cart_quantity = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                      '.qty-input-text > input')))
                    cart_quantity = cart_quantity.get_attribute('placeholder')
                except TimeoutException:
                    self.log_err('Not found quantity')
                    cart_quantity = 0

            self.product_cart_quantity = str(cart_quantity)
            cart_product_price = self.browser.find_element(By.CSS_SELECTOR, '.new-cart-item-sell-price > span').text
            cart_product_price = cart_product_price.replace('$', '')
            self.product_cart_price = str(round(float(cart_product_price)/int(cart_quantity), 2))

            cart_product_option_id = self.browser.find_element(By.CSS_SELECTOR, '.vendor > span.ng-scope').text

            cart_product_option_id = cart_product_option_id.split('#')[-1]

            if cart_product_option_id == self.option_id:

                self.log_info(f'Id in the cart correct - {cart_product_option_id}')
                if int(cart_quantity) == int(self.count):

                    self.log_info(f'Quantity in the cart correct - {cart_quantity}')
                    single_product_price = round(float(cart_product_price)/int(cart_quantity), 2)
                    if float(single_product_price) == float(self.product_price):

                        self.log_info(f'Single product price in the cart correct - {single_product_price}')
                        self.product_status = 'SUCCESS'
                        self.take_screenshot('cart_is_correct')
                    else:

                        self.log_err(f'Single product price in the cart incorrect - {single_product_price}')
                        self.product_status = 'WRONG_DATA'
                        self.take_screenshot('cart_is_incorrect')
                        return None
                else:

                    self.log_err(f'Quantity in the cart incorrect - {cart_quantity}')
                    self.product_status = 'WRONG_DATA'
                    self.take_screenshot('cart_is_incorrect')
                    return None
            else:

                self.log_err(f'Id in the cart incorrect {cart_product_option_id}')
                self.product_status = 'WRONG_ITEM'
                self.take_screenshot('cart_is_incorrect')
                return None
        else:

            self.log_err(f'In cart {len(cart_items)} products')
            self.product_status = 'WRONG_DATA'
            self.take_screenshot('cart_is_incorrect')
            return None

    def take_screenshot(self, msg=''):
        dir_name = os.path.join(settings.MEDIA_ROOT, 'status_image')
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        screenshot_name = self.screenshot + msg + '.png'
        self.browser.save_screenshot(os.path.join(dir_name, screenshot_name))
        self.screenshot_dict[msg] = screenshot_name
        self.log_info(f'Save screenshot {msg} \n{dir_name}/{screenshot_name}\n{self.browser.current_url}')

    def run(self):

        self.log_info('Open main page')
        self.browser.get(self.main_page_url)
        self.open_cart_page()
        self.clear_cart()

        if self.cart_status == 'EMPTY':
            self.log_info('Start add product to cart')
            self.browser.get(self.product_url)
            try:
                self.add_product_to_cart()
            except (TimeoutException, StaleElementReferenceException, ElementNotInteractableException):
                self.log_err('Some exception when add to cart. Return status ADDING_PROBLEM')
                self.browser.quit()
                return {
                    'quantity': self.product_cart_quantity,
                    'price': self.product_cart_price,
                    'order_status': 'ADDING_PROBLEM',
                    'screenshots': self.screenshot_dict
                }
            self.log_info(f'Order status {self.product_status}. Close browser')
            self.browser.quit()
            return {
                'quantity': self.product_cart_quantity,
                'price': self.product_cart_price,
                'order_status': self.product_status,
                'screenshots': self.screenshot_dict
            }

        else:
            self.product_status = 'ADDING_PROBLEM'
            self.log_info(f'Order status {self.product_status}. Close browser')
            self.browser.quit()
            return {
                'quantity': self.product_cart_quantity,
                'price': self.product_cart_price,
                'order_status': self.product_status,
                'screenshots': self.screenshot_dict
            }
