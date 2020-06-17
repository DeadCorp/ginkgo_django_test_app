# -*- coding: utf-8 -*-
import asyncio
import json
from urllib.parse import urljoin
import scrapy
import re
from ..items import ProductItem
from task.models import Task

loop = asyncio.get_event_loop()


class WalmartSpider(scrapy.Spider):
    start_time = loop.time()
    name = 'walmart'
    handle_httpstatus_list = [520, 404]
    allowed_domains = ['walmart.com']
    walmart_url = 'https://walmart.com/ip/'
    selected = '?selected=true'
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapers.pipelines.WalmartProductPipeline': 300,
        },
    }

    def __init__(self, task_id):
        self.task = Task.objects.get(id=task_id)
        self.supplier = 'WM'
        self.to_parse = json.loads(self.task.data)
        self.to_parse = self.to_parse[self.supplier]
        self.parsed_count = 0
        self.sku_storage = []

    def start_requests(self):
        for product in self.to_parse:
            if product['id']:
                yield scrapy.Request(
                    url=urljoin(self.walmart_url, product['id'] + self.selected),
                    callback=self.parse,
                    meta=product
                )

    def parse(self, response):
        product_id = response.meta.get('id')
        item = ProductItem()
        item['supplier'] = response.meta.get('supplier')
        item['market'] = response.meta.get('market')
        item['letter'] = response.meta.get('letter')
        item['quantity'] = response.meta.get('quantity')
        item['option_id'] = response.meta.get('option')
        if response.status not in self.handle_httpstatus_list:
            item['brand'] = response.css("span[itemprop='brand']::text").get(default='is unknown')
            item['category'] = response.css('ol.breadcrumb-list span::text').getall()
            item['description'] = response.css('div #about-product-section *::text').getall()
            item['name'] = response.css("h1[itemprop='name']::text").get(default='is unknown')
            item['price'] = response.css("span[itemprop='price']::attr(content)").get(default='is unknown')
            item['variants_tag'] = response.css("div.varslabel>span::text").getall()
            item['img'] = response.css("[itemprop='image']::attr(src)").get(default='is unknown')
            availability = response.css("div[class*='oos'] *::text").get()
            availability_count = 'is unknown'
            if availability is None:
                availability = response.css("div[class*='urgency'] *::text").get()
                if availability is None:
                    availability = 'In availability'
                else:
                    availability_count = self.take_num(availability)
            item['rating'] = response.css("div.ReviewsRating-container div[aria-hidden='true'] *::text").getall()
            item['delivery_price'] = ''.join(response.css("div.prod-fulfillment-messaging-text *::text").getall())
            item['product_id'] = product_id
            item['url'] = response.url
            item['available'] = availability
            item['available_count'] = availability_count
            self.parsed_count += 1
            yield item
        else:
            item['product_id'] = product_id
            item['name'] = 'not found'
            item['delivery_price'] = 'not found'  # need set not null name and delivery to correct ordering in view

            yield item

    @staticmethod
    def take_num(line):
        response = re.findall(r'\d*\.\d+|\d+', line)
        return response

    def close(spider, reason):
        end_time = loop.time()
        total_time = end_time - spider.start_time
        scrap_time = 'Spent time from scraping: {total_time} ' \
                     'seconds  Found {parsed_count} of {count_to_parse} product'

        task = Task.objects.filter(id=spider.task.id)
        new_text = json.loads(task[0].data)

        task_time_text = task[0].description

        if task_time_text != 'In progress...':
            numbers_from_task = spider.take_num(task_time_text)
            time_from_task = numbers_from_task[0]
            parsed_count = numbers_from_task[1]
            count_to_parse = numbers_from_task[2]
            format_dict = {
                'parsed_count': str(int(parsed_count) + int(spider.parsed_count)),
                'count_to_parse': str(int(count_to_parse) + len(spider.to_parse)),
                'total_time': str(float(time_from_task) + total_time)
            }
            scrap_time = scrap_time.format(**format_dict)
            for sku in spider.sku_storage:
                new_text.append(sku)
        else:
            format_dict = {
                'parsed_count': spider.parsed_count,
                'count_to_parse': len(spider.to_parse),
                'total_time': total_time
            }
            scrap_time = scrap_time.format(**format_dict)
            new_text = [sku for sku in spider.sku_storage]

        task.update(description=scrap_time, data=json.dumps(new_text))


