# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re

from bs4 import BeautifulSoup

UNKNOWN = 'is unknown'


class WalmartProductPipeline(object):
    free = 'Free delivery'
    free_2 = 'Free 2-day delivery'
    fake_free = 'Free delivery on $35+'
    in_stoke_only = 'in-store purchase only'
    no_available_delivery = 'Delivery not available'
    no_delivery = 'No delivery'
    default_delivery = '$5.99'

    def process_item(self, item, spider):
        item['delivery'] = True
        item['shipping'] = True
        item['store_pickup'] = True

        if item['name'] != 'not found' and item['price'] != 'is unknown':
            price_for_delivery = item['price']
            item['price'] = '$' + item['price']

            if item['available'] != 'Out of stock':
                if (self.in_stoke_only not in item['delivery_price']) and (
                        self.no_available_delivery not in item['delivery_price']):
                    if float(price_for_delivery) >= 35.0:
                        item['delivery_price'] = self.free
                    elif (self.fake_free not in item['delivery_price']) and (self.free_2 not in item['delivery_price']):
                        item['delivery_price'] = self.free
                    else:
                        item['delivery_price'] = self.default_delivery
                else:
                    item['delivery_price'] = self.no_delivery
            else:
                item['delivery_price'] = self.no_delivery
        elif item['price'] == 'is unknown':
            item['delivery_price'] = self.no_delivery
        if len(item['description']) != 0:
            item['description'] = ''.join(item['description'])
            item['description'] = re.sub(r'<button[^>]*>([\s\S]*?)<\/button>', '', item['description'])
        else:
            item['description'] = 'is unknown'
        item['category'] = ''.join(item['category']) if len(item['category']) != 0 else 'is unknown'
        item['rating'] = " Star ".join(item['rating']) if len(item['rating']) != 0 else 'is unknown'

        variants_dict = {}
        if len(item['variants_tag']) == 0:
            variants_dict = 'is unknown'
            item['variants_tag'] = variants_dict
        else:
            for x, i in enumerate(item['variants_tag']):
                if x % 2 == 0:
                    variants_dict[i] = item['variants_tag'][x + 1]
            variant_list = [k+v for k, v in variants_dict.items()]
            item['variants_tag'] = '; '.join(variant_list)
        item['img'] = item['img'].replace('//', '') if item['img'] is not None else None
        item = create_sku(item, spider)
        item.save()
        return item


class KmartProductPipeline(object):

    def process_item(self, item, spider):
        item['product_id'] = UNKNOWN if not item['product_id'] else item['product_id']
        item = create_sku(item, spider)
        if item.get('available', UNKNOWN) != UNKNOWN:
            if item.get('price', UNKNOWN) != UNKNOWN:
                if item['available']:
                    item['available'] = 'In availability'
                    item['delivery_price'] = 'Free delivery' if int(item['price']) > 59 else '6.49'
                else:
                    item['available'] = 'Out of stock'
                    item['delivery_price'] = 'No delivery'
        else:
            item['available'] = 'Out of stock'
            item['delivery_price'] = 'No delivery'

        variants_tag = []
        if item.get('variants_tag', UNKNOWN) != UNKNOWN:
            for tag in item['variants_tag']:
                variants_tag.append(tag['name'] + ' : ' + tag['value'])
            item['variants_tag'] = '; '.join(variants_tag)

        if item.get('category', UNKNOWN) != UNKNOWN:
            category = ' / '.join(item['category'])
            item['category'] = category
        item['description'] = ''.join(item['description']) if item.get('description') else UNKNOWN
        item.save()

        return item


def create_sku(item, spider):
    item['sku'] = '_'.join([item["market"], item['supplier'], item['product_id']])
    item['sku'] += '#' + item['option_id'] if item['option_id'] else ''
    item['sku'] += '-' + item['letter'] if item['letter'] is not None else ''
    item['sku'] += '$' + str(item['quantity']) if item['quantity'] else ''
    item['option_id'] = UNKNOWN if not item['option_id'] else item['option_id']
    spider.sku_storage.append(item['sku'])
    return item


class SamsClubProductPipeline(object):

    def process_item(self, item, spider):
        item = create_sku(item, spider)
        if item.get('category'):
            soup = BeautifulSoup(item['category'], 'html.parser')
            categories = soup.select('ol.sc-breadcrumbs > li')
            if categories is not None:
                category = [category.text for category in categories]
                item['category'] = ' / '.join(category)

        item['available'] = 'Availability' if item.get('available') in ['inStoke', 'inStock', 'lowInStock'] else 'Out of stock'
        if not item.get('shipping'):
            item['shipping'] = True if item['available'] == 'Availability' else False
        item['delivery_price'] = 'Free delivery' if item.get('delivery_price') == 0 else item.get('delivery_price')

        item.save()
        return item
