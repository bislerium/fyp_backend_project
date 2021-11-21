from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from .forms import *


# Create your views here.


class CustomLoginView(LoginView):

    def get_success_url(self):
        # print(self.request.user)
        if self.request.user.is_admin:
            return f'admin/{self.request.user.full_name}'
        return f'staff/{self.request.user.full_name}'


def admin_index(request, id):
    return render(request, 'core/admin/admin-home.html', context={'id':id})


def staff_index(request, id):
    return render(request, 'core/staff/staff-home.html', context={'id':id})


def create_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was created for ' + form.data['full_name'])
            return HttpResponse('User Created')
    context = {
        'form': StaffCreationForm()
    }
    return render(request, 'core/auth/register.html', context)


def create_NGO(request):
    if request.method == 'POST':
        form = NGOCreationForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was created for ' + form.data['full_name'])
            return HttpResponse('User Created')
    context = {
        'form': NGOCreationForm()
    }
    return render(request, 'core/auth/register.html', context)
