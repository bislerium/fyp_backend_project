from django.contrib.auth.forms import UserCreationForm
from django import forms

from core.models import *


class StaffCreationForm(UserCreationForm):
    # class Meta:
    #     model = Staff
    #     fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'citizenship_photo',
    #               'is_active', 'display_picture', 'username', 'email', 'password1', 'password2']
    #     widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}
    pass


class NGOCreationForm(UserCreationForm):
    # class Meta:
    #     model = NGOUser
    #     fields = ['full_name', 'establishment_date', 'fields_of_work', 'phone', 'address', 'display_picture',
    #               'e_pay_number', 'bank', 'email', 'password1', 'password2', ]
    #     widgets = {'establishment_date': forms.DateInput(attrs={'type': 'date'}),
    #                'fields_of_work': forms.SelectMultiple, }
    pass
