import json
import subprocess
from pathlib import Path

from django.conf import settings
from django.db import models

from product.utils import parse_sku
from supplieraccount.models import SupplierCodes


class Task(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User', default=1)
    description = models.TextField(verbose_name='Description', default='', blank=True)
    data = models.TextField(verbose_name='Task data', default='')

    def save(self):
        data = set(self.data.split())
        sorted_sku = sort_sku_by_suppliers(parse_data(data))
        self.data = json.dumps(sorted_sku)
        super(Task, self).save()

        for supplier_code in sorted_sku:
            if len(sorted_sku[supplier_code]) != 0:
                supplier = SupplierCodes.SUPPLIERS[supplier_code]
                run_spider(self, supplier)

    def __str__(self):
        return f'{self.user_id} task: {self.pk}'


def run_spider(task_instance, supplier):
    path_to_spiders = str(Path(__file__).parent) + '/scrapers/scrapers/spiders/'
    subprocess.Popen(["scrapy", "crawl", supplier.lower(), '-a', f'task_id={task_instance.id}'], cwd=path_to_spiders)
    Task.objects.filter(user_id=task_instance.user_id, id=task_instance.id).update(description='In progress...')


def parse_data(data):
    return [parse_sku(sku) for sku in data]


# def sort_sku_by_suppliers(list_data):
#     result_dict = {}
#     for supplier_code in SupplierCodes.SUPPLIERS:
#         result_dict[supplier_code] = [item for item in list_data if item['supplier'] == supplier_code]
#
#     return result_dict
def sort_sku_by_suppliers(list_data):
    return {supplier_code: [item for item in list_data if item['supplier'] == supplier_code] for supplier_code in
            SupplierCodes.SUPPLIERS}
