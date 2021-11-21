from django.contrib.auth.forms import UserCreationForm
from django.forms import forms

from core.models import *


class StaffCreationForm(UserCreationForm):
    class Meta:
        model = AdministrativeUser
        fields = ['username', 'email', 'full_name', 'date_of_birth', 'gender', 'phone', 'address', 'citizenship_photo',
                  'is_active', 'display_picture', 'password1', 'password2']


class NGOCreationForm(UserCreationForm):
    class Meta:
        model = NGOUser
        fields = '__all__'
