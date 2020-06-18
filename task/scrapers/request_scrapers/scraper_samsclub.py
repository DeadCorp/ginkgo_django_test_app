import json
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from product.models import Product


logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')


class SamsClubScraper(object):
    API_SEARCH_URL = 'https://www.samsclub.com/api/node/vivaldi/v1/products/search/?sourceType=1&sortKey=relevance' \
                     '&sortOrder=1&limit=48&searchTerm={search_id}&clubId=6454&br=true'
    PRODUCT_DATA_URL = 'https://www.samsclub.com/api/soa/services/v1/catalog/product/{product_id}?' \
                       'response_group=LARGE&clubId=6454'
    SHIPPING_DATA_URL = 'https://www.samsclub.com/api/node/vivaldi/v2/products/shipping/{product_id}/{sku_id}/' \
                        '{zip_code}?optimizeShipTypes=true'
    SAMS_CLUB_URL = 'http://samsclub.com'

    UNKNOWN = 'is_unknown'

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'authid': 'aA0NvvAIrVJY0vXTc99mQQ==',
    }

    def __init__(self, list_to_parse):

        # self.task = Task.objects.get(id=task_id)
        # self.supplier = 'SC'
        # self.to_parse = json.loads(self.task.data)
        # self.to_parse = self.to_parse[self.supplier]
        self.to_parse = list_to_parse
        self.item = {
            'sku': '',
            'product_id': '',
            'option_id': '',
            'name': '',
            'price': '',
            'url': '',
            'category': '',
            'rating': '',
            'available': '',
            'brand': '',
            'available_count': '',
            'delivery_price': '',
            'variants_tag': '',
            'img': '',
            'supplier': '',
            'model': '',
            'description': '',
            'is_variant': False,
            'delivery': False,
            'shipping': False,
            'store_pickup': False,
        }
        self.additional_item = {
            'sku_id': '',
            'free_shipping_flag': '',
        }
        self.session = requests.Session()
        self.session.headers = self.headers

    def check_product_exist(self, product):
        response = self.session.get(self.API_SEARCH_URL.format(**{'search_id': product['id']}))
        data = json.loads(response.text)
        payload = data.get('payload', {})
        if payload is not {}:
            records = payload.get('records') or []
            if len(records) == 1:
                product_id = records[0].get('productId')
                if product_id == product['id']:
                    logging.info(f'Product {product_id} found, id is correct')
                else:
                    logging.error(f'Found incorrect product - id {product_id}')
                    self.not_found_product(product)
            else:
                logging.error(f'Product {product["id"]} not found')
                self.not_found_product(product)
        else:
            logging.error(f'Product {product["id"]} not found')
            self.not_found_product(product)

    def not_found_product(self, product):
        self.item['name'] = 'not found'
        self.item['available'] = False
        self.item['delivery_price'] = 'No delivery'
        self.create_sku(product)

    def take_option_data(self, sku_options, product):
        sku_data = {}
        if self.item['is_variant']:
            if len(sku_options) > 0:
                for product_option in sku_options:
                    if product_option.get('itemNumber', self.UNKNOWN) == product['option']:
                        sku_data = product_option
                        self.item['model'] = sku_data.get('modelNo', self.UNKNOWN)
                        inventory_options = sku_data.get('inventoryOptions') or []
                        if len(inventory_options) == 1:
                            self.item['available'] = inventory_options[0].get('status', self.UNKNOWN)
                            self.item['available_count'] = inventory_options[0].get('availableToSellQuantity',
                                                                                    self.UNKNOWN)
                        pricing_options = sku_data.get('pricingOptions') or []
                        if len(pricing_options) == 1:
                            self.item['price'] = pricing_options[0].get('finalPrice', {}).get('currencyAmount',
                                                                                              self.UNKNOWN)
                        variance = sku_data.get('varianceValueMap', {})
                        variants_tag = []
                        for key, value_dict in variance.items():
                            variants_tag.append(f'{value_dict.get("varianceNameOriginal", self.UNKNOWN)}: '
                                                f'{value_dict.get("varianceValue", self.UNKNOWN)}')
                        self.item['variants_tag'] = variants_tag

                        break
        else:
            if len(sku_options) == 1:
                if sku_options[0].get('itemNumber', self.UNKNOWN) == product['option']:
                    sku_data = sku_options[0]
                    self.item['variants_tag'] = self.UNKNOWN
        self.additional_item['sku_id'] = sku_data.get('skuId', self.UNKNOWN)
        self.item['name'] = sku_data.get('skuName', self.UNKNOWN)
        self.item['img'] = sku_data.get('listImage', self.UNKNOWN)
        self.additional_item['free_shipping_flag'] = sku_data.get('freeShippingFlag', self.UNKNOWN)

    def take_product_data(self, product):
        response = self.session.get(self.PRODUCT_DATA_URL.format(**{'product_id': product['id']}))
        data = json.loads(response.text)
        payload = data.get('payload', {})
        if payload is not {}:
            self.item['is_variant'] = payload.get('varianceTemplateProduct', self.UNKNOWN)
            sku_options = payload.get('skuOptions') or []
            self.take_option_data(sku_options, product)
            self.item['model'] = payload.get('modelNumber', self.UNKNOWN) if not self.item['model'] else self.item[
                'model']
            self.item['brand'] = payload.get('brandName', self.UNKNOWN)
            self.item['description'] = payload.get('shortDescription', self.UNKNOWN)
            self.item[
                'rating'] = f'Star - {payload.get("reviewRating", self.UNKNOWN)},' \
                            f' reviews - {payload.get("reviewCount", self.UNKNOWN)}'

            if payload.get('clubPricing', {}) == {}:
                self.item['price'] = payload.get('onlinePricing', {}).get('finalPrice').get('currencyAmount',
                                                                                            self.UNKNOWN)
                self.item['available'] = payload.get('onlineInventory', {}).get('status', self.UNKNOWN)
                self.item['available_count'] = payload.get('onlineInventory', {}).get('availableToSellQuantity',
                                                                                      self.UNKNOWN)
                self.item['shipping'] = True
                self.item['store_pickup'] = False

            else:
                self.item['shipping'] = False
                self.item['store_pickup'] = True
                self.item['delivery_price'] = 'No delivery'

            self.item['product_id'] = product['id']
            self.item['option_id'] = product['option']
            self.item['supplier'] = product['supplier']
            self.item['url'] = urljoin(self.SAMS_CLUB_URL, payload.get('seoUrl', self.UNKNOWN))

    def take_category(self):
        product_page_response = self.session.get(self.item['url'])
        soup = BeautifulSoup(product_page_response.text, 'html.parser')
        categories = soup.select('ol.sc-breadcrumbs > li')
        category = [category.text for category in categories]
        self.item['category'] = '/'.join(category)

    def take_shipping_data(self, product):
        shipping_response = self.session.get(self.SHIPPING_DATA_URL.format(**{'zip_code': '60169',
                                                                              'product_id': product['id'],
                                                                              'sku_id': self.additional_item['sku_id']}))
        shipping_payload = json.loads(shipping_response.text)
        shipping = shipping_payload.get('payload', {}).get('shippingEstimates', [])
        if len(shipping) == 1:
            if self.item['delivery_price'] != 'No delivery':
                self.item['delivery_price'] = shipping[0].get('shipCost', {}).get('currencyAmount', self.UNKNOWN) \
                    if not self.additional_item['free_shipping_flag'] else 0

    def create_sku(self, product):
        self.item['sku'] = '_'.join([product["market"], product['supplier'], product['id']])
        self.item['sku'] += '#' + product['option'] if product['option'] else ''
        self.item['sku'] += ('-' + product['letter']) if product['letter'] is not None else ''
        self.item['sku'] += ('$' + str(product['quantity'])) if product['quantity'] else ''

    def run(self):
        for product in self.to_parse:
            self.check_product_exist(product)
            if self.item['name'] != 'not found':
                self.take_product_data(product)
                self.take_category()
                self.take_shipping_data(product)
                self.create_sku(product)
            new_product = Product(**self.item)
            new_product.save()
