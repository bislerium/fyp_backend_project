import django_filters

from .models import *


class NGOFilter(django_filters.FilterSet):
    CHOICES = (
        ('Name', 'Name'),
        ('Est. Date', 'Est. Date'),
    )
    ngo_filter_by = django_filters.ChoiceFilter(choices=CHOICES, method='ngo_filter_by_')

    class Meta:
        model = NGOUser
        fields = {
            'full_name': ['icontains'],
        }

    def ngo_filter_by_(self, queryset, name, value):
        if value == self.CHOICES['Name']:
            return queryset.order_by('full_name')
        if value == self.CHOICES['Est. Date']:
            return queryset.order_by('establishment_date')
        # if value in FIELD_OF_WORK:
