from django.contrib import admin

from task.models import Task


@admin.register(Task)
class AdminTask(admin.ModelAdmin):
    list_display = ['id', 'user_id']
