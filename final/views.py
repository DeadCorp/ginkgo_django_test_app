from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from final.forms import RegisterForm


def index(request):
    return redirect('product:products')


def register(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
            login(request, user)
        else:
            form = RegisterForm()
            wrong = 'Invalid data'
            return render(request, 'registration/register.html', {'form': form, 'wrong': wrong})
        if request.POST.get('next') == ('/accounts/login/' or 'accounts/register/'):
            return redirect('product:products')
        else:
            return redirect(request.POST.get('next'))
    else:

        if request.user.is_anonymous:
            form = RegisterForm()
        else:
            return redirect('product:products')

    return render(request, 'registration/register.html', {'form': form})
