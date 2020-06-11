from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from supplieraccount.models import SupplierCodes
from task.forms import TaskForm
from task.models import Task


@login_required()
def refresh_product_data(request, sku):
    obj = Task(user_id=request.user, data=sku)
    obj.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER') + '#' + sku)


@login_required()
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get('next'):
                return redirect(request.POST.get('next'))
        return redirect('product:products')
    else:
        form = TaskForm()
        tasks = Task.objects.filter(user_id=request.user).order_by('-id')[:5]

    suppliers = SupplierCodes.SUPPLIERS
    return render(request, 'task/add_task.html', {'form': form, 'tasks': tasks, 'suppliers': suppliers})


@login_required()
def delete_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        try:
            task = Task.objects.get(pk=task_id)
            task.delete()
        except Task.DoesNotExist:
            pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
