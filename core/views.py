from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView

from .forms import *


def forbidden_page(request):
    return render(request, 'core/extensions/403-page.html')


def page_not_found(request):
    return render(request, 'core/extensions/404-page.html')


# Create your views here.

class CustomLoginView(LoginView):

    def get_success_url(self):
        user_: User = self.request.user
        if user_.is_staff and user_.is_superuser:
            return reverse_lazy('admin-home')
        if user_.groups.filter(name=Group.objects.get(name__iexact='People')).exists() or \
                user_.groups.filter(name=Group.objects.get(name__iexact='NGO')).exists():
            return reverse_lazy('forbid')
        if user_.groups.filter(name=Group.objects.get(name__iexact='Staff')).exists():
            return reverse_lazy('staff-home')


def admin_index(request):
    return render(request, 'core/admin/admin-home.html', context={'pk': request.user.username})


def staff_index(request):
    return render(request, 'core/staff/staff-home.html', context={'pk': request.user.username})


# Staff Crud

def create_staff(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        staff_form = StaffCreationForm(request.POST, request.FILES or None)
        if user_form.is_valid() and staff_form.is_valid():
            user_form.save()
            staff_form_ = staff_form.save(commit=False)
            staff_form_.account = User.objects.get(username=user_form.data['username'])
            staff_form_.save()
            messages.success(request, f'Account created for {staff_form.data["full_name"]}')
            return redirect('read-staffs')
    context = {
        'form1': UserCreationForm(),
        'form2': PeopleCreationForm(),
    }
    return render(request, 'core/staff/staff-create.html', context)


class read_staffs(ListView):
    model = Staff
    # paginate_by = 20
    template_name = 'core/staff/staffs-read.html'


class read_staff(DetailView):
    model = Staff
    template_name = 'core/staff/staff-read.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.get('object').reviewed_posts = self.get_object().report_review.filter(review=True).count()
        return context


class update_staff(UpdateView):
    model = Staff
    form_class = StaffCreationForm
    template_name = 'core/staff/staff-update.html'
    success_url = reverse_lazy('read-staffs')


class delete_staff(DeleteView):
    model = Staff
    success_url = reverse_lazy('read-staffs')


# People CRUD

class read_peoples(ListView):
    model = PeopleUser
    # paginate_by = 20
    template_name = 'core/user/peoples-read.html'


class read_people(DetailView):
    model = PeopleUser
    template_name = 'core/user/people-read.html'


class update_people(UpdateView):
    model = PeopleUser
    form_class = PeopleCreationForm
    template_name = 'core/user/people-update.html'
    success_url = reverse_lazy('read-peoples')


class delete_people(DeleteView):
    model = PeopleUser
    success_url = reverse_lazy('read-peoples')


# NGO Crud

def create_ngo(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        ngo_form = NGOCreationForm(request.POST, request.FILES or None)
        if user_form.is_valid() and ngo_form.is_valid():
            user_form.save()
            ngo_form_ = ngo_form.save(commit=False)
            ngo_form_.account = User.objects.get(username=user_form.data['username'])
            ngo_form_.save()
            messages.success(request, f'Account created for {ngo_form.data["full_name"]}')
            return redirect('read-ngos')
    context = {
        'form1': UserCreationForm(),
        'form2': NGOCreationForm(),
    }
    return render(request, 'core/ngo/ngo-create.html', context)


class read_ngos(ListView):
    model = NGOUser
    # paginate_by = 20
    template_name = 'core/ngo/ngos-read.html'


class read_ngo(DetailView):
    model = NGOUser
    template_name = 'core/ngo/ngo-read.html'


class update_ngo(UpdateView):
    model = NGOUser
    form_class = NGOCreationForm
    template_name = 'core/ngo/ngo-update.html'
    success_url = reverse_lazy('read-ngos')


class delete_ngo(DeleteView):
    model = NGOUser
    success_url = reverse_lazy('read-ngos')
