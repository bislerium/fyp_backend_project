from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView

from .forms import *


# Create your views here.


class CustomLoginView(LoginView):

    def get_success_url(self):
        # print(self.request.user)
        if self.request.user.is_admin:
            return reverse_lazy('admin-home')
        return reverse_lazy('staff-home')


def admin_index(request):
    return render(request, 'core/admin/admin-home.html', context={'pk': request.user.username})


def staff_index(request):
    return render(request, 'core/staff/staff-home.html', context={'pk': request.user.username})


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


# User CRUD
class read_users(ListView):
    model = NormalUser
    paginate_by = 20
    template_name = 'core/user/users-read.html'


class read_user(DetailView):
    model = NormalUser
    template_name = 'core/user/user-read.html'


class update_user(UpdateView):
    model = NormalUser
    fields = '__all__'
    template_name = 'core/user/user-update.html'
    success_url = reverse_lazy('read-users')


class delete_user(DeleteView):
    model = NormalUser
    success_url = reverse_lazy('read-users')
