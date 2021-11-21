from django.contrib.auth.forms import UserCreationForm
from django import forms

from core.models import *


class StaffCreationForm(UserCreationForm):
    class Meta:
        model = AdministrativeUser
        fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'citizenship_photo',
                  'is_active', 'display_picture', 'username', 'email', 'password1', 'password2']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class NGOCreationForm(UserCreationForm):
    class Meta:
        model = NGOUser
        fields = '__all__'
