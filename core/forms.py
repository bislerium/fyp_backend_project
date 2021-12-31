from django import forms

from core.models import *


class StaffCreationForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'date_of_birth', 'gender', 'phone', 'address', 'display_picture', 'citizenship_photo',
                  'is_married']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class NGOCreationForm(forms.ModelForm):
    class Meta:
        model = NGOUser
        fields = ['full_name', 'establishment_date', 'field_of_work', 'phone', 'address', 'display_picture',
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

        fields = ['post', 'reason', 'action', 'is_reviewed']
        widgets = {'reason': forms.Textarea(attrs={'rows': '12'}),
                   'post': forms.HiddenInput(), 'is_reviewed': forms.HiddenInput()}
