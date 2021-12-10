from django import forms

from core.models import *


class StaffCreationForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'display_picture', 'citizenship_photo',
                  'marital_status']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class NGOCreationForm(forms.ModelForm):
    class Meta:
        model = NGOUser
        fields = ['full_name', 'establishment_date', 'field_of_work', 'phone', 'address', 'display_picture',
                  'epay_account', 'swc_affl_cert', 'pan_cert', 'verified', ]
        widgets = {'establishment_date': forms.DateInput(attrs={'type': 'date'}), }


class PeopleCreationForm(forms.ModelForm):
    class Meta:
        model = PeopleUser
        fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'display_picture',
                  'citizenship_photo', 'verified']
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

        fields = ['post', 'reason', 'action', 'review']
        widgets = {'reason': forms.Textarea(attrs={'rows': '12'}),
                   'post': forms.HiddenInput(), 'review': forms.HiddenInput()}
