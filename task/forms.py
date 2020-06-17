from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Task
from django import forms


class TaskForm(ModelForm):

    user_id = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Task
        fields = ['user_id', 'data']
