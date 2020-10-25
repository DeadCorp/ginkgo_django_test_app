import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from task.forms import TaskForm
from task.generate_report import ReportData, ReportFile
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
    form = TaskForm()
    return render(request, 'task/add_task.html', {'form': form})


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
        data_generator = ReportData(request, pk)
        field_names = data_generator.task_field_names
        data = data_generator.generate_task_data()
        path_to_file = data_generator.create_file_path('scrapy', 'task', 'csv')

        file_generator = ReportFile(data, field_names, path_to_file)
        file_generator.generate_csv_file()

        if os.path.exists(path_to_file):
            response = FileResponse(open(path_to_file, 'rb'))
            return response
        # return check_generated_errors(data_generator)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def task_gen_xls(request, pk):
    if request.method == 'POST':
        data_generator = ReportData(request, pk)
        field_names = data_generator.task_field_names
        data = data_generator.generate_task_data()
        path_to_file = data_generator.create_file_path('scrapy', 'task', 'xls')

        file_generator = ReportFile(data, field_names, path_to_file)
        file_generator.generate_xls_file()

        if os.path.exists(path_to_file):
            response = FileResponse(open(path_to_file, 'rb'))
            return response
        # return check_generated_errors(data_generator, path_to_file)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def check_generated_errors(data_generator):
    return add_task(data_generator.take_request_with_errors())
