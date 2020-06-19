# -*- coding: utf-8 -*-
import asyncio
import json
import re
from urllib.parse import urljoin

import scrapy

from .walmart import WalmartSpider
from ..items import ProductItem
from task.models import Task

loop = asyncio.get_event_loop()


class SamsClubSpider(scrapy.Spider):
    start_time = loop.time()
    name = 'samsclub'
    handle_httpstatus_list = [400]
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapers.pipelines.SamsClubProductPipeline': 500,
        },
    }
    API_SEARCH_URL = 'https://www.samsclub.com/api/node/vivaldi/v1/products/search/?sourceType=1&sortKey=relevance' \
                     '&sortOrder=1&limit=48&searchTerm={product_id}&clubId=6454&br=true'
    PRODUCT_DATA_URL = 'https://www.samsclub.com/api/soa/services/v1/catalog/product/{product_id}?' \
                       'response_group=LARGE&clubId=6454'
    SHIPPING_DATA_URL = 'https://www.samsclub.com/api/node/vivaldi/v2/products/shipping/{product_id}/{sku_id}/' \
                        '{zip_code}?optimizeShipTypes=true'
    SAMS_CLUB_URL = 'http://samsclub.com'

    UNKNOWN = 'is unknown'
    ZIP_CODE = '60169'

    def __init__(self, task_id):
        self.task = Task.objects.get(id=task_id)
        self.supplier = 'SC'
        self.to_parse = json.loads(self.task.data)[self.supplier]
        self.parsed_count = 0
        self.sku_storage = []

    def start_requests(self):
        for product in self.to_parse:
            if not product['id'] and not product['option']:
                continue
            item = ProductItem()
            item['supplier'] = product['supplier']
            item['market'] = product['market']
            item['letter'] = product['letter']
            item['quantity'] = product['quantity']
            item['product_id'] = product['id']
            item['option_id'] = product['option']

            temp_dict = {
                'product_id': product['id'],
            }

            yield scrapy.Request(
                url=self.API_SEARCH_URL.format(**temp_dict),
                callback=self.check_product_exist,
                meta={'item': item}
            )

    def check_product_exist(self, response):
        item = response.meta.get('item')
        self.logger.info(f'{item["product_id"]} Start check product existing')

        data = json.loads(response.body)
        payload = data.get('payload', {})
        if payload is not {}:
            records = payload.get('records') or []
            if len(records) == 1:
                product_id = records[0].get('productId')
                if product_id == item['product_id']:
                    self.logger.info(f'Product {product_id} found, id is correct')
                else:
                    self.logger.error(f'Found incorrect product - id {product_id}')
                    self.not_found_product(item)
            else:
                self.logger.error(f'Product {item["product_id"]} not found')
                self.not_found_product(item)
        else:
            self.logger.error(f'Product {item["product_id"]} not found')
            self.not_found_product(item)

        yield scrapy.Request(
            url=self.PRODUCT_DATA_URL.format(**item),
            callback=self.take_product_data,
            meta={'item': item}
        )

    @staticmethod
    def not_found_product(item):
        item['name'] = 'not found'
        item['available'] = False
        item['delivery_price'] = 'No delivery'
        yield item
        return None

    def take_product_data(self, response):
        item = response.meta.get('item')
        self.logger.info(f'{item["product_id"]} - Start take product data')

        data = json.loads(response.body)
        payload = data.get('payload', {})
        if payload is not {}:
            self.logger.info(f'{item["product_id"]} - Product data is not empty')
            item['is_variant'] = payload.get('varianceTemplateProduct', self.UNKNOWN)
            item['model'] = payload.get('modelNumber', self.UNKNOWN)
            item['brand'] = payload.get('brandName', self.UNKNOWN)
            item['description'] = payload.get('shortDescription', self.UNKNOWN)
            item['rating'] = f'Star - {round(payload.get("reviewRating", self.UNKNOWN), 1)},' \
                             f' reviews - {payload.get("reviewCount", self.UNKNOWN)}'
            if not item['is_variant']:
                if payload.get('onlinePricing', {}) != {}:
                    self.logger.info(f'{item["product_id"]} - Product have online pricing')
                    item['price'] = payload.get('onlinePricing', {}).get('finalPrice', {}).get('currencyAmount', self.UNKNOWN)
                    item['available'] = payload.get('onlineInventory', {}).get('status', self.UNKNOWN)
                    item['available_count'] = payload.get('onlineInventory', {}).get('availableToSellQuantity', self.UNKNOWN)
                    item['shipping'] = True
                    item['store_pickup'] = False
                else:
                    self.logger.info(f'{item["product_id"]} - Product not have online pricing.'
                                     f' Take not accurate price. No shipping')
                    item['price'] = payload.get('clubPricing', {}).get('finalPrice', {}).get('currencyAmount', self.UNKNOWN)
                    item['shipping'] = False
                    item['store_pickup'] = True
                    item['delivery_price'] = 'No delivery'
            item['url'] = urljoin(self.SAMS_CLUB_URL, payload.get('seoUrl', self.UNKNOWN))

            sku_options = payload.get('skuOptions') or []
            item = self.take_option_data(sku_options, item)

            yield scrapy.Request(
                url=item['url'],
                callback=self.take_category,
                meta={'item': item}
            )

    def take_option_data(self, sku_options, item):
        self.logger.info(f'{item["product_id"]} - Start take option data')
        sku_data = {}
        if item['is_variant']:
            self.logger.info(f'{item["product_id"]} - Product is variance')
            if len(sku_options) > 0:
                for product_option in sku_options:
                    if product_option.get('itemNumber', self.UNKNOWN) == item['option_id']:
                        self.logger.info(f'{item["product_id"]} - Take variance specific data')
                        sku_data = product_option
                        item['model'] = sku_data.get('modelNo', self.UNKNOWN)
                        inventory_options = sku_data.get('inventoryOptions') or []
                        if len(inventory_options) == 1:
                            item['available'] = inventory_options[0].get('status', self.UNKNOWN)
                            item['available_count'] = inventory_options[0].get('availableToSellQuantity',
                                                                               self.UNKNOWN)
                        pricing_options = sku_data.get('pricingOptions') or []
                        if len(pricing_options) == 1:
                            item['price'] = pricing_options[0].get('finalPrice', {}).get('currencyAmount',
                                                                                         self.UNKNOWN)
                        variance = sku_data.get('varianceValueMap', {})
                        variants_tag = []
                        for key, value_dict in variance.items():
                            variants_tag.append(f'{value_dict.get("varianceNameOriginal", self.UNKNOWN)}: '
                                                f'{value_dict.get("varianceValue", self.UNKNOWN)}')
                        item['variants_tag'] = '; '.join(variants_tag)

                        break
        else:
            self.logger.info(f'{item["product_id"]} - Product is not variance')
            if len(sku_options) == 1:
                if sku_options[0].get('itemNumber', self.UNKNOWN) == item['option_id']:
                    sku_data = sku_options[0]
                    item['variants_tag'] = self.UNKNOWN
        self.logger.info(f'{item["product_id"]} - Take common option data')
        item['sku_id'] = sku_data.get('skuId', self.UNKNOWN)
        item['name'] = sku_data.get('skuName', self.UNKNOWN)
        item['img'] = sku_data.get('listImage', self.UNKNOWN)
        item['free_shipping_flag'] = sku_data.get('freeShippingFlag', self.UNKNOWN)

        return item

    def take_category(self, response):
        item = response.meta.get('item')
        self.logger.info(f'{item["product_id"]} - Take product category')
        item['category'] = response.body

        yield scrapy.Request(
            url=self.SHIPPING_DATA_URL.format(**{'zip_code': self.ZIP_CODE,
                                                 'product_id': item['product_id'],
                                                 'sku_id': item['sku_id']}),
            callback=self.take_shipping_data,
            meta={'item': item}
        )

    def take_shipping_data(self, response):
        item = response.meta.get('item')
        self.logger.info(f'{item["product_id"]} - Take shipping data')
        if response.status not in self.handle_httpstatus_list:
            shipping = json.loads(response.body).get('payload', {}).get('shippingEstimates', [])
            if len(shipping) != 0 and item.get('delivery_price') != 'No delivery':
                if not item['free_shipping_flag']:
                    costs = [i.get('shipCost', {}).get('currencyAmount', 123456789) for i in shipping]
                    item['delivery_price'] = min(costs)
                else:
                    item['delivery_price'] = 0
        else:
            self.logger.info(f'{item["product_id"]} - Response code - 400. Set no shipping')
            item['shipping'] = False
            item['delivery_price'] = 'No delivery'

        self.parsed_count += 1
        yield item

    @staticmethod
    def close(spider, reason):
        WalmartSpider.close(spider, reason)
