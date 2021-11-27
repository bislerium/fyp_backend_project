from django.contrib.auth.forms import UserCreationForm
from django import forms

from core.models import *


class StaffCreationForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'citizenship_photo', 'display_picture',
                  'marital_status']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class NGOCreationForm(forms.ModelForm):
    class Meta:
        model = NGOUser
        fields = ['full_name', 'establishment_date', 'field_of_work', 'phone', 'address', 'display_picture',
                  'epay_account', ]
        widgets = {'establishment_date': forms.DateInput(attrs={'type': 'date'}),
                   'field_of_work': forms.SelectMultiple(attrs={'size': 8}), }


class BankCreationForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = '__all__'
