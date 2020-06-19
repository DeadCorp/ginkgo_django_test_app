# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from product.models import Product


class ProductItem(DjangoItem):
    django_model = Product
    # create temp fields, using it only for scrape
    market = scrapy.Field()
    letter = scrapy.Field()
    quantity = scrapy.Field()
    uid = scrapy.Field()
    sku_id = scrapy.Field()
    free_shipping_flag = scrapy.Field()
