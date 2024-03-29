from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.models import *


class ALPImageForm(forms.ModelForm):
    class Meta:
        model = AppImage
        fields = '__all__'


class DownLinkForm(forms.Form):
    downlink_url = forms.URLField(required=False, label='App Download Link',
                                  widget=forms.URLInput(attrs={'placeholder': 'link', 'value': 'https://'}))


class StaffCreationForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'display_picture', 'citizenship_photo',
                  'is_married']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")


class NGOCreationForm(forms.ModelForm):
    class Meta:
        model = NGOUser
        fields = ['full_name', 'establishment_date', 'field_of_work', 'phone', 'address', 'latitude', 'longitude',
                  'display_picture',
                  'epay_account', 'swc_affl_cert', 'pan_cert', 'is_verified', ]
        widgets = {'establishment_date': forms.DateInput(attrs={'type': 'date'}), }


class PeopleCreationForm(forms.ModelForm):
    class Meta:
        model = PeopleUser
        fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'display_picture',
                  'citizenship_photo', 'is_verified']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'}), }


class BankCreationForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = '__all__'


class ReportForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs["maxlength"] = 950
        self.fields['reason'].required = True
        self.fields['action'].required = True

    class Meta:
        model = Report
        fields = ['reason', 'action']
        widgets = {'reason': forms.Textarea(attrs={'rows': '10'}), }
