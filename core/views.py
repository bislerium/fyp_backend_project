from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, CreateView

from .forms import *


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

class read_peoples(ListView):
    model = PeopleUser
    paginate_by = 20
    template_name = 'core/user/peoples-read.html'


class read_people(DetailView):
    model = PeopleUser
    template_name = 'core/user/people-read.html'


class update_people(UpdateView):
    model = PeopleUser
    fields = '__all__'
    template_name = 'core/user/people-update.html'
    success_url = reverse_lazy('read-peoples')


class delete_people(DeleteView):
    model = PeopleUser
    success_url = reverse_lazy('read-peoples')


def forbid(request):
    return render(request, 'core/extensions/forbidden-page.html')


# NGO Crud
def testCreate(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        ngo_form = NGOCreationForm(request.POST, request.FILES or None)
        form3 = BankCreationForm(request.POST)
        if user_form.is_valid() and ngo_form.is_valid():
            user_form.save()
            ngo_form_ = ngo_form.save(commit=False)
            ngo_form_.account = User.objects.get(username=user_form.data['username'])
            if form3.is_valid():
                form3.save()
            ngo_form_.save()
            messages.success(request, f'Account created for {ngo_form_.data["full_name"]}')
            return redirect('read-ngos')
    user_form = UserCreationForm()
    ngo_form = NGOCreationForm()
    form3 = BankCreationForm()
    context = {
        'form1': user_form,
        'form2': ngo_form,
        'form3': form3,
    }
    return render(request, 'core/test.html', context)


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
