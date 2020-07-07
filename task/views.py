import csv
import json
import os
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from product.models import Product
from supplieraccount.models import SupplierCodes
from task.forms import TaskForm
from task.models import Task


@login_required()
def refresh_product_data(request, sku):
    # create new task with 1 sku for update product data
    obj = Task(user_id=request.user, data=sku)
    obj.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER') + '#' + sku)


@login_required()
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('task:add_task')
    else:
        form = TaskForm()
        tasks = Task.objects.filter(user_id=request.user).order_by('-id')
    if request.META.get('wrong'):
        wrong = request.META.get('wrong')
    else:
        wrong = ''
    suppliers = SupplierCodes.SUPPLIERS
    return render(request, 'task/add_task.html', {'form': form, 'tasks': tasks, 'suppliers': suppliers, 'wrong': wrong})


@login_required()
def delete_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        try:
            task = Task.objects.get(pk=task_id)
            task.delete()
        except Task.DoesNotExist:
            pass
    return redirect('task:add_task')


@login_required()
def retry_task(request, pk):
    try:
        task = Task.objects.get(pk=pk)
        task.data = ' '.join(json.loads(task.data))
        task.save()
    except Task.DoesNotExist:
        pass
    return redirect(reverse('task:add_task') + '#' + pk)


@login_required()
def task_gen_csv(request, pk):
    if request.method == 'POST':
        task_instance = Task.objects.get(pk=pk)
        task_data = json.loads(task_instance.data)

        dir_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/scrapy_task_csv')
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        file_name = f'Scrapy_task_{pk}_generated_{datetime.datetime.now()}.csv'

        with open(os.path.join(dir_name, file_name), mode='w') as file:
            field_names = ['SKU', 'Availability', 'Item price', 'Delivery price', 'Total price', 'Quantity']
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()
            for sku in task_data:
                try:
                    product = Product.objects.get(sku=sku)
                except Product.DoesNotExist:
                    wrong = {'task_error_id': task_instance.pk,
                             'error': f'Product with SKU - {sku} dont exist in data base.\n'
                                      f'Click to Retry task for get this product in data base.',
                            }
                    request.method = 'GET'
                    request.META['wrong'] = wrong
                    return add_task(request)
                available = product.available if product.delivery_price != 'No delivery' else 'Out of stock'
                to_write = {
                    'SKU': product.sku,
                    'Availability': available,
                }
                if available == 'Out of stock':
                    to_write.update({key: 0 for key in field_names if key not in to_write.keys()})
                else:
                    delivery_price = product.delivery_price if product.delivery_price != 'Free delivery' else 0.00
                    to_write.update({
                        'Item price': product.price,
                        'Delivery price': delivery_price,
                        'Total price': round(float(product.price) + float(delivery_price), 2),
                        'Quantity': product.available_count if product.available_count != 'is unknown' else 1,
                    })
                writer.writerow(to_write)
        if os.path.exists(os.path.join(dir_name, file_name)):
            response = FileResponse(open(os.path.join(dir_name, file_name), 'rb'))
            return response
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
