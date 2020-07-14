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


class KmartSpider(scrapy.Spider):
    start_time = loop.time()
    name = 'kmart'
    allowed_domains = ['kmart.com']
    start_urls = ['http://kmart.com/']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapers.pipelines.KmartProductPipeline': 400,
        },
    }
    API_SEARCH_URL = 'https://www.kmart.com/service/search/v2/productSearch?catalogId=10104&keyword={product_id}&' \
                     'rmMattressBundle=true&searchBy=keyword&storeId=10151&tabClicked=All&zip={zip_code}'
    PRODUCT_SEARCH_URL = 'https://www.kmart.com/search={product_id}'
    PRODUCT_URL = 'https://www.kmart.com/content/pdp/config/products/v1/products/{product_id}?site=kmart'
    PRODUCT_RATING_URL = 'https://www.kmart.com/content/pdp/ratings/single/search/Kmart/{product_id}'
    PRODUCT_OFFER_URL = 'https://www.kmart.com/content/pdp/v1/products/{product_id}/' \
                        'variations/{uid}/offers/{option_id}?site=kmart'
    PRODUCT_PRICE_URL = 'https://www.kmart.com/content/pdp/products/pricing/v2/get/price/display/' \
                        'json?offer={option_id}&priceMatch=Y&memberType=G&urgencyDeal=Y&site=KMART&zipCode={zip_code}'
    KMART_URL = 'https://www.kmart.com/'
    UNKNOWN = 'is unknown'
    ZIP_CODE = '60169'

    def __init__(self, task_id):
        self.task = Task.objects.get(id=task_id)
        self.supplier = 'KM'
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
            if not product['id']:
                self.logger.info(f'Product id not give. Search product id for option id {product["option"]}')
                temp_dict = {'product_id': product['option']}
            else:
                self.logger.info(
                    f'Have product id - {product["id"]}, option id - {product["option"]}. Search product data')
                temp_dict = {'product_id': product['id']}

            product['item'] = item

            yield scrapy.Request(
                url=self.PRODUCT_SEARCH_URL.format(**temp_dict),
                callback=self.search_id_follow_request,
                meta=product
            )

    def search_id_follow_request(self, response):
        temp_dict = {
            'product_id': response.meta.get('option') if not response.meta.get('id') else response.meta.get('id'),
            'zip_code': self.ZIP_CODE
        }

        yield response.follow(
            url=self.API_SEARCH_URL.format(**temp_dict),
            callback=self.found_id_and_parse,
            meta=response.meta
        )

    def found_id_and_parse(self, response):
        item = response.meta.get('item')
        id_data = json.loads(response.body)

        product_id = id_data.get('data', {}).get('products') or []
        if len(product_id) > 0:
            item['name'] = product_id[0].get('name', self.UNKNOWN)
            part_number = product_id[0].get('partNumber', self.UNKNOWN)
            product_id = product_id[0].get('sin', self.UNKNOWN)
            item['product_id'] = product_id
            item['option_id'] = response.meta.get('option') or part_number

        else:
            self.logger.error('not found')
            item['product_id'] = response.meta.get('id')
            item['option_id'] = response.meta.get('option')
            item['name'] = 'not found'
            item['delivery_price'] = 'No delivery'
            item['available'] = False
            yield item
            return None

        yield from self.product_request(self.PRODUCT_URL.format(**dict(item)), item)

    def product_request(self, url, item):
        yield scrapy.Request(
            url=url,
            callback=self.parse_product,
            meta={'item': item}
        )

    def price_request(self, url, item):
        yield scrapy.Request(
            url=url,
            callback=self.parse_price,
            meta={'item': item},
            headers={'authid': 'aA0NvvAIrVJY0vXTc99mQQ=='}
        )

    def rating_request(self, url, item):
        yield scrapy.Request(
            url=url,
            callback=self.parse_rating,
            meta={'item': item}
        )

    def offer_request(self, url, item):
        yield scrapy.Request(
            url=url,
            callback=self.parse_offer,
            meta={'item': item}
        )

    def take_data_from_status_section(self, item, data):
        status = data['productstatus']
        item['is_variant'] = status.get('isVariant', self.UNKNOWN)
        item['available_count'] = status.get('offerCount', self.UNKNOWN)
        item['uid'] = status.get('uid', self.UNKNOWN)
        return item

    def take_data_from_variant_section(self, item, data):
        variant_section = data.get('attributes', {}).get('variants', self.UNKNOWN)
        if variant_section != self.UNKNOWN:
            for product in variant_section:
                if product['offerId'] == item['option_id']:
                    self.logger.info('product found')
                    item['uid'] = product['uid']
                    tags = product.get('attributes', self.UNKNOWN)
                    if tags != self.UNKNOWN:
                        item['variants_tag'] = [tag for tag in tags]
                    break
            else:
                # if product variant not available now, we cant take uid and  variants tag
                # but can take current info in self.parse_offer
                self.logger.error('variant with excepted option_id not found')
        return item

    def take_data_from_category_section(self, item, data):
        category_section = data['productmapping']['primaryWebPath']
        item['category'] = [category['name'] for category in category_section]
        return item

    def take_data_from_product_section(self, item, data):
        product_section = data['product']
        item['img'] = (
            product_section.get('assets', {}).get('imgs', {})[0]['vals'][0].get('src', self.UNKNOWN)
        )
        item['name'] = product_section.get('name', self.UNKNOWN)
        item['model'] = product_section.get('mfr', {}).get('modelNo', self.UNKNOWN)
        item['brand'] = product_section.get('brand', {}).get('name', self.UNKNOWN)
        item['description'] = [desc.get('val', self.UNKNOWN) for desc in
                               product_section.get('desc', {})]
        return item

    def take_data_from_rating_section(self, item, data):
        rating_section = data.get('data', self.UNKNOWN)
        if rating_section != self.UNKNOWN:
            over_all = rating_section.get('overall_rating', self.UNKNOWN)
            review_count = rating_section.get('review_count', self.UNKNOWN)
            item['rating'] = (f'{over_all} star {review_count} reviews'
                              if over_all != self.UNKNOWN else 'No rating'
                              )
            return item

    def take_data_from_price_section(self, item, data):
        price = data.get('priceDisplay', {}).get('response') or []
        if len(price) > 0:
            price = price[0].get('finalPrice', {}).get('numeric', self.UNKNOWN)
            item['price'] = price
        else:
            item['price'] = self.UNKNOWN
        return item

    def take_data_from_offer_section(self, item, data):
        offer_section = data.get('data', self.UNKNOWN)
        if offer_section != self.UNKNOWN:
            offer_status = offer_section.get('offerstatus', self.UNKNOWN)
            offer_mapping = offer_section.get('offermapping', {}).get('fulfillment', self.UNKNOWN)
            option_id = offer_status.get('offerId', self.UNKNOWN)
            if option_id != self.UNKNOWN and option_id == item['option_id']:
                self.logger.info('Offer id is correct')

                if item['uid'] == self.UNKNOWN:
                    item['uid'] = offer_status.get('uid', self.UNKNOWN)
                    tags_section = offer_section.get('offer', {}).get('definingAttrs', {})
                    if len(tags_section) > 0:
                        item['variants_tag'] = [{tag['attr']['name']: tag['val']['name']} for tag in tags_section]

                item['available'] = offer_status.get('isAvailable', self.UNKNOWN)
                item['shipping'] = offer_mapping.get('shipping', self.UNKNOWN)
                item['store_pickup'] = offer_mapping.get('storepickup', self.UNKNOWN)
                item['delivery'] = offer_mapping.get('delivery', self.UNKNOWN)

            else:
                self.logger.error('Offer id is not correct')
        return item

    def parse_product(self, response):
        item = response.meta.get('item')
        item['product_url'] = urljoin(self.KMART_URL, f'-/p-{item["product_id"]}')
        self.logger.info(f'Parse product - response {response}')
        data_json = json.loads(response.body)

        data = data_json['data']

        self.logger.info('Start take data from status section')
        item = self.take_data_from_status_section(item, data)
        self.logger.info('End take data from status section')

        if item['is_variant']:
            if not item['option_id']:
                item['option_id'] = 'incorrect option id'
                yield item
                return None
            self.logger.info('it`s variant product')
            self.logger.info('start search excepted product')
            item = self.take_data_from_variant_section(item, data)

        item = self.take_data_from_category_section(item, data)

        self.logger.info('Start take data from product section')
        item = self.take_data_from_product_section(item, data)
        self.logger.info('End take data from product section')

        yield from self.rating_request(self.PRODUCT_RATING_URL.format(**dict(item)), item)

    def parse_price(self, response):
        item = response.meta.get('item')
        self.logger.info('Start search product price')
        data = json.loads(response.body)
        item = self.take_data_from_price_section(item, data)
        self.logger.info('End search product price')

        url_offer = self.PRODUCT_OFFER_URL.format(**dict(item))

        yield from self.offer_request(url_offer, item)

    def parse_rating(self, response):
        item = response.meta.get('item')
        data = json.loads(response.body)
        self.logger.info('start take rating data')
        item = self.take_data_from_rating_section(item, data)
        self.logger.info('end take rating data')

        dict_item = {
            'option_id': item['option_id'],
            'zip_code': self.ZIP_CODE,
        }
        url_price = self.PRODUCT_PRICE_URL.format(**dict_item)
        yield from self.price_request(url_price, item)

    def parse_offer(self, response):
        item = response.meta.get('item')
        data = json.loads(response.body)
        self.logger.info('Start take offer data')
        item = self.take_data_from_offer_section(item, data)
        self.logger.info('End take offer data')
        self.parsed_count += 1

        yield item

    @staticmethod
    def close(spider, reason):
        WalmartSpider.close(spider, reason)


