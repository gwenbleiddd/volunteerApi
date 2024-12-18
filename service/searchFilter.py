import django_filters
from .models import Opportunity

class OpportunityFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains', label='Location')
    required_skills = django_filters.CharFilter(field_name='required_skills', lookup_expr='icontains', label='Skills Required')
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte', label='Start Date')
    end_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte', label='End Date')

    class Meta:
        model = Opportunity
        fields = ['location', 'required_skills', 'start_date', 'end_date']
