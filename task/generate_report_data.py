import datetime
import json
import os

from product.models import Product
from task.models import Task


class ReportData(object):

    def __init__(self, task_id, request):
        self.task_instance = Task.objects.get(pk=task_id)
        self.task_data = json.loads(self.task_instance.data)
        self.request = request
        self.request.method = 'GET'
        self.generated_list = []
        self.wrong = {'task_error_id': self.task_instance.pk,
                      'error': [],
                      }

    @property
    def field_names(self):
        return ['SKU', 'Availability', 'Item price', 'Delivery price', 'Total price', 'Quantity']

    def generate(self):

        for sku in self.task_data:
            to_write = {
                'SKU': sku,
            }
            try:
                product = Product.objects.get(sku=sku)
                available = product.available if product.delivery_price != 'No delivery' else 'Out of stock'
                to_write.update({
                    'Availability': available,
                })
                if available == 'Out of stock':
                    to_write.update({key: 0 for key in self.field_names if key not in to_write.keys()})
                else:
                    delivery_price = product.delivery_price if product.delivery_price != 'Free delivery' else 0.00
                    to_write.update({
                        'Item price': product.price,
                        'Delivery price': delivery_price,
                        'Total price': round(float(product.price) + float(delivery_price), 2),
                        'Quantity': product.available_count if product.available_count != 'is unknown' else 1,
                    })
            except Product.DoesNotExist:
                self.add_error(sku)
                to_write.update({key: 'No product in data base' for key in self.field_names if key not in to_write.keys()})
            self.generated_list.append(to_write)

        if len(self.wrong['error']) != 0:
            self.add_error(last=True)

        return self.generated_list

    def add_error(self, sku=None, last=False):
        self.wrong['error'].append(f'Product with SKU - {sku} dont exist in data base.\n' if not last else
                                   f'Click to Retry task for get this product in data base.')
        self.request.META.update(self.wrong)

    def take_request_with_errors(self):
        return self.request

    def create_file_path(self, end):
        dir_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'media/scrapy_task_{end}')
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        file_name = f'Scrapy_task_{self.task_instance.pk}_generated_{datetime.datetime.now()}.{end}'
        path_to_file = os.path.join(dir_name, file_name)
        return path_to_file
