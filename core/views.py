from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, CreateView

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


# Staff Crud

def create_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was created for ' + form.data['full_name'])
            return redirect('read-staffs')
    context = {
        'form': StaffCreationForm()
    }
    return render(request, 'core/staff/staff-create.html', context)


class read_staffs(ListView):
    model = Staff
    paginate_by = 20
    template_name = 'core/staff/staffs-read.html'


class read_staff(DetailView):
    model = Staff
    template_name = 'core/staff/staff-read.html'


class update_staff(UpdateView):
    model = Staff
    fields = '__all__'
    template_name = 'core/staff/staff-update.html'
    success_url = reverse_lazy('read-staffs')


class delete_staff(DeleteView):
    model = Staff
    success_url = reverse_lazy('read-staffs')


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


def forbid(request):
    return render(request, 'core/extensions/forbidden-page.html')


# NGO Crud

class create_ngo(CreateView):
    form_class = NGOCreationForm
    model = NGOUser
    template_name = 'core/ngo/ngo-create.html'
    success_url = reverse_lazy('read-ngos')


class read_ngos(ListView):
    model = NGOUser
    # paginate_by = 20
    template_name = 'core/ngo/ngos-read.html'


class read_ngo(DetailView):
    model = NGOUser
    template_name = 'core/ngo/ngo-read.html'


class update_ngo(UpdateView):
    model = NGOUser
    fields = '__all__'
    template_name = 'core/ngo/ngo-update.html'
    success_url = reverse_lazy('read-ngos')


class delete_ngo(DeleteView):
    model = NGOUser
    success_url = reverse_lazy('read-ngos')

    # def delete(self, request, *args, **kwargs):
    #     # User.delete(id=)
    #     return super().delete(request, *args, **kwargs)


